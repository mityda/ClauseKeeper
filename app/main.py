"""
ClauseKeeper — FastAPI application.

Routes:
  GET  /                  landing page (pitch + links)
  GET  /scan             free compliance scanner form
  POST /scan             run scanner on pasted text OR fetched URL -> scorecard
  GET  /pricing          pricing page + Stripe subscribe (or stub fallback)
  POST /subscribe        Stripe Checkout Session (or dev stub if no keys)
  GET  /success          verify Checkout session, upsert user, log in
  POST /webhook/stripe   Stripe webhook: flip per-user subscription state
  GET  /login            login page (dev: email login; Stripe: portal link)
  POST /login            dev/no-Stripe email login
  GET  /logout           clear session cookie
  GET  /portal           Stripe Customer Portal redirect
  GET  /generate         paid doc-generator form (gated on logged-in subscriber)
  POST /generate         build + persist docs, redirect to hosted policy URL
  GET  /p/{pid}          hosted policy bundle (stable URL)
  GET  /p/{pid}/{doc}    single document view (privacy|terms|cookies|ai)
  GET  /api/health       JSON health check
  POST /api/scan         JSON scanner endpoint (for curl/automation tests)
"""
import os
from datetime import date

import httpx
from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .scanner import scan_text, html_to_text
from .generator import generate_documents, CLAUSE_LIBRARY_VERSION, CLAUSE_CHANGELOG, DISCLAIMER
from . import store
from . import auth

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app = FastAPI(title="ClauseKeeper", version="0.1.0")
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

PLAN = "always-current-19"


def _clause_last_updated() -> str:
    """Human-friendly date for the current clause library freshness signal."""
    return date.today().strftime("%B %d, %Y")


def _badge_grade(score: int) -> str:
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 50:
        return "C"
    if score >= 30:
        return "D"
    return "F"


def _normalize_badge_score(score: int | str) -> int:
    try:
        value = int(score)
    except (TypeError, ValueError):
        value = 0
    return max(0, min(100, value))


def _badge_color(grade: str) -> str:
    return {
        "A": "#0F9F6E",
        "B": "#0F9F6E",
        "C": "#B7791F",
        "D": "#C2410C",
        "F": "#C2410C",
    }.get(grade, "#14B8A6")


@app.on_event("startup")
def _startup():
    store.init_db()


# ---------------------------------------------------------------- helpers
def _stripe():
    """Configure and return the stripe module, or None if no secret key is set."""
    if not os.environ.get("STRIPE_SECRET_KEY"):
        return None
    import stripe
    stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
    return stripe


def _user(request: Request):
    return auth.current_user(request)


async def _fetch_url_text(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    async with httpx.AsyncClient(follow_redirects=True, timeout=15.0,
                                 headers={"User-Agent": "ClauseKeeperScanner/0.1"}) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return html_to_text(resp.text)


# ---------------------------------------------------------------- pages
@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    user = _user(request)
    return templates.TemplateResponse(request, "landing.html", {
        "subscribed": bool(user and user["subscribed"]),
        "user": user,
        "clause_version": CLAUSE_LIBRARY_VERSION,
        "clause_last_updated": _clause_last_updated(),
    })


@app.get("/scan", response_class=HTMLResponse)
def scan_form(request: Request):
    return templates.TemplateResponse(request, "scan.html", {"result": None})


@app.post("/scan", response_class=HTMLResponse)
async def scan_run(request: Request, mode: str = Form("text"),
                   policy_text: str = Form(""), url: str = Form("")):
    error = None
    raw = ""
    source = None
    if mode == "url" and url.strip():
        try:
            raw = await _fetch_url_text(url.strip())
            source = url.strip()
        except Exception as e:
            error = f"Could not fetch that URL: {e}"
    else:
        raw = policy_text
        source = "pasted text"

    result = scan_text(raw) if raw and not error else None
    return templates.TemplateResponse(request, "scan.html", {
        "result": result, "error": error,
        "source": source, "submitted_text": policy_text, "submitted_url": url,
    })


@app.get("/pricing", response_class=HTMLResponse)
def pricing(request: Request):
    user = _user(request)
    return templates.TemplateResponse(request, "pricing.html", {
        "subscribed": bool(user and user["subscribed"]),
        "user": user,
        "stripe_enabled": auth.stripe_enabled(),
    })


@app.get("/about", response_class=HTMLResponse)
def about(request: Request):
    user = _user(request)
    return templates.TemplateResponse(request, "about.html", {
        "subscribed": bool(user and user["subscribed"]),
        "user": user,
    })


@app.get("/badge", response_class=HTMLResponse)
def badge_builder(request: Request):
    """Educational page: explains the badge, shows the grading scale, and a
    clearly-labeled SAMPLE. The real embeddable badge is earned via a scan."""
    scale = [
        {"grade": "A", "range": "85–100", "color": _badge_color("A"),
         "label": "Strong", "implies": "Current, thorough coverage incl. 2026 AI-disclosure. Minor freshness checks only."},
        {"grade": "B", "range": "70–84", "color": _badge_color("B"),
         "label": "Decent", "implies": "Solid foundation but missing some 2026-critical clauses."},
        {"grade": "C", "range": "50–69", "color": _badge_color("C"),
         "label": "Gaps", "implies": "Notable gaps — likely not fully 2026-compliant."},
        {"grade": "D", "range": "30–49", "color": _badge_color("D"),
         "label": "Weak", "implies": "Major clauses missing or outdated. Needs real work."},
        {"grade": "F", "range": "0–29", "color": _badge_color("F"),
         "label": "At risk", "implies": "Little to no compliant language detected."},
    ]
    return templates.TemplateResponse(request, "badge.html", {
        "scale": scale,
        "sample_src": "/badge.svg?sample=1&score=92",
    })


@app.post("/badge/mint")
def badge_mint(request: Request, score: int = Form(...), source: str = Form("")):
    """Mint a verified badge from a REAL scan result and return the embed code.

    Called from the scan results page after an actual scan — the score is the
    one our scanner produced, not a user-supplied value on a public URL.
    """
    score = _normalize_badge_score(score)
    grade = _badge_grade(score)
    domain = (source or "").strip()[:120] or None
    bid = store.create_badge(score=score, grade=grade, domain=domain, source=domain)
    badge_url = f"https://clausekeeper.app/badge/v/{bid}.svg"
    embed_code = (
        f'<a href="https://clausekeeper.app/scan" aria-label="Verified by ClauseKeeper">'
        f'<img src="{badge_url}" '
        f'alt="ClauseKeeper verified compliance score: {score}/100, grade {grade}" '
        f'width="300" height="70"></a>'
    )
    return templates.TemplateResponse(request, "badge_minted.html", {
        "score": score, "grade": grade, "badge_id": bid,
        "badge_url": badge_url, "embed_code": embed_code,
    })


def _render_badge_svg(score: int, grade: str, *, sample: bool = False, verified_date: str | None = None) -> str:
    """Build the badge SVG. Either a watermarked SAMPLE or a verified badge with a date."""
    color = _badge_color(grade)
    if sample:
        tag = "SAMPLE"
    elif verified_date:
        tag = f"Verified · {verified_date}"
    else:
        tag = "Verified"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="70" viewBox="0 0 300 70" role="img" aria-label="ClauseKeeper Compliance Score: {score} out of 100, grade {grade}{' (sample)' if sample else ''}">
  <defs>
    <linearGradient id="g" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#2DD4BF"/><stop offset="1" stop-color="#14B8A6"/></linearGradient>
    <filter id="s" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="6" stdDeviation="6" flood-color="#0B2237" flood-opacity=".14"/></filter>
  </defs>
  <rect x="2" y="2" width="296" height="66" rx="16" fill="#fff" stroke="#E2E8F0" filter="url(#s)"/>
  <circle cx="36" cy="35" r="20" fill="url(#g)"/>
  <path d="M27 35.5l6 6 12-14" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="66" y="25" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif" font-size="13" font-weight="700" fill="#5B7488">ClauseKeeper</text>
  <text x="66" y="43" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif" font-size="15" font-weight="800" fill="#0B2237">Compliance Score</text>
  <text x="66" y="57" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif" font-size="9" font-weight="700" fill="{'#B7791F' if sample else '#0F9F6E'}" letter-spacing=".3">{tag}</text>
  <rect x="232" y="12" width="54" height="46" rx="13" fill="{color}"/>
  <text x="259" y="34" text-anchor="middle" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif" font-size="16" font-weight="900" fill="#fff">{score}</text>
  <text x="259" y="49" text-anchor="middle" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif" font-size="10" font-weight="800" fill="#fff">Grade {grade}</text>
</svg>'''


@app.get("/badge.svg")
def badge_svg(sample: int = 1, score: int = 92):
    """Public badge endpoint — serves ONLY a watermarked SAMPLE for the education page.

    Real, embeddable badges are unforgeable and served by verification id at
    /badge/v/<id>.svg after an actual scan. Arbitrary ?score= can no longer mint
    a 'verified'-looking badge.
    """
    score = _normalize_badge_score(score)
    grade = _badge_grade(score)
    svg = _render_badge_svg(score, grade, sample=True)
    return Response(svg, media_type="image/svg+xml", headers={"Cache-Control": "public, max-age=3600"})


@app.get("/badge/v/{bid}.svg")
def badge_verified_svg(bid: str):
    """Serve a verified badge from a stored scan result. Tamper-proof: the score
    comes from our DB, not the URL."""
    rec = store.get_badge(bid)
    if not rec:
        # Unknown id → render an explicit 'unverified' marker, not a fake score.
        svg = _render_badge_svg(0, "F", sample=True)
        return Response(svg, media_type="image/svg+xml", status_code=404,
                        headers={"Cache-Control": "no-store"})
    date = (rec.get("verified_at") or "")[:10]
    svg = _render_badge_svg(rec["score"], rec["grade"], verified_date=date)
    return Response(svg, media_type="image/svg+xml", headers={"Cache-Control": "public, max-age=1800"})


# ---------------------------------------------------------------- auth / billing
@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse(request, "login.html", {
        "stripe_enabled": auth.stripe_enabled(),
        "error": None,
    })


@app.post("/login")
def login_submit(request: Request, email: str = Form("")):
    """Dev/no-Stripe email login. In Stripe mode this is disabled in favor of the portal."""
    if auth.stripe_enabled():
        # Real identity comes from Stripe Checkout; don't allow self-asserted email login.
        return RedirectResponse("/portal", status_code=303)

    email = (email or "").strip().lower()
    if not email or "@" not in email:
        return templates.TemplateResponse(request, "login.html", {
            "stripe_enabled": False,
            "error": "Please enter a valid email address.",
        }, status_code=400)

    user = store.upsert_user(email)
    resp = RedirectResponse("/generate", status_code=303)
    auth.set_session_cookie(resp, user["id"])
    return resp


@app.get("/logout")
def logout():
    resp = RedirectResponse("/", status_code=303)
    auth.clear_session_cookie(resp)
    return resp


def _normalize_plan(plan: str) -> str:
    """Return a safe billing plan value for checkout/dev subscription flows."""
    return "monthly" if (plan or "").strip().lower() == "monthly" else "annual"


def _stripe_price_id_for_plan(plan: str) -> str | None:
    if plan == "monthly":
        return os.environ.get("STRIPE_PRICE_ID_MONTHLY") or os.environ.get("STRIPE_PRICE_ID")
    return os.environ.get("STRIPE_PRICE_ID_ANNUAL")


@app.post("/subscribe")
def subscribe(request: Request, email: str = Form(""), plan: str = Form("annual")):
    """Create a Stripe Checkout Session (subscription). Falls back to a dev stub
    when STRIPE_SECRET_KEY is absent so local dev stays fully testable."""
    stripe = _stripe()
    plan = _normalize_plan(plan)

    if stripe is None:
        # ----- DEV STUB: no Stripe keys. Mark a (possibly anonymous) user subscribed. -----
        user = _user(request)
        if user is None:
            # No session yet: behave like login + subscribe with a placeholder dev email.
            email = (email or "").strip().lower() or "dev@example.com"
            user = store.upsert_user(email)
        store.set_subscribed(user["id"], True, PLAN)
        resp = RedirectResponse("/generate", status_code=303)
        auth.set_session_cookie(resp, user["id"])
        return resp

    # ----- REAL STRIPE CHECKOUT -----
    price_id = _stripe_price_id_for_plan(plan)
    if not price_id:
        env_name = "STRIPE_PRICE_ID_MONTHLY" if plan == "monthly" else "STRIPE_PRICE_ID_ANNUAL"
        raise HTTPException(status_code=500, detail=f"{env_name} not configured")

    kwargs = dict(
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=f"{auth.APP_BASE_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{auth.APP_BASE_URL}/pricing",
        allow_promotion_codes=True,
    )
    email = (email or "").strip().lower()
    if email:
        kwargs["customer_email"] = email

    session = stripe.checkout.Session.create(**kwargs)
    return RedirectResponse(session.url, status_code=303)


@app.get("/success", response_class=HTMLResponse)
def checkout_success(request: Request, session_id: str = ""):
    """Verify the Checkout session server-side, upsert the user, log them in."""
    stripe = _stripe()
    if stripe is None or not session_id:
        return RedirectResponse("/pricing", status_code=303)

    try:
        cs = stripe.checkout.Session.retrieve(session_id)
    except Exception:
        return RedirectResponse("/pricing", status_code=303)

    # Resolve email + customer from the verified session.
    email = (cs.get("customer_details") or {}).get("email") or cs.get("customer_email")
    customer_id = cs.get("customer")
    paid = cs.get("payment_status") == "paid" or cs.get("status") == "complete"

    if not email:
        return RedirectResponse("/pricing", status_code=303)

    user = store.upsert_user(email, customer_id)
    if paid:
        store.set_subscribed(user["id"], True, PLAN)

    resp = RedirectResponse("/generate", status_code=303)
    auth.set_session_cookie(resp, user["id"])
    return resp


@app.get("/portal")
def portal(request: Request):
    """Redirect a returning customer to the Stripe Customer Portal."""
    stripe = _stripe()
    user = _user(request)
    if stripe is None:
        return RedirectResponse("/login", status_code=303)
    if not user or not user.get("stripe_customer_id"):
        return RedirectResponse("/pricing", status_code=303)
    ps = stripe.billing_portal.Session.create(
        customer=user["stripe_customer_id"],
        return_url=f"{auth.APP_BASE_URL}/pricing",
    )
    return RedirectResponse(ps.url, status_code=303)


@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Verify the Stripe signature and flip per-user subscription state."""
    stripe = _stripe()
    if stripe is None:
        return JSONResponse({"error": "stripe not configured"}, status_code=400)

    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    if not webhook_secret:
        return JSONResponse({"error": "STRIPE_WEBHOOK_SECRET not configured"}, status_code=400)

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except Exception as e:
        return JSONResponse({"error": f"signature verification failed: {e}"}, status_code=400)

    etype = event["type"]
    obj = event["data"]["object"]

    if etype == "checkout.session.completed":
        email = (obj.get("customer_details") or {}).get("email") or obj.get("customer_email")
        customer_id = obj.get("customer")
        if email:
            user = store.upsert_user(email, customer_id)
            store.set_subscribed(user["id"], True, PLAN)
        elif customer_id:
            store.set_subscribed_by_customer(customer_id, True, PLAN)

    elif etype == "invoice.paid":
        customer_id = obj.get("customer")
        if customer_id:
            store.set_subscribed_by_customer(customer_id, True, PLAN)

    elif etype in ("customer.subscription.deleted", "invoice.payment_failed"):
        customer_id = obj.get("customer")
        if customer_id:
            store.set_subscribed_by_customer(customer_id, False)

    return JSONResponse({"received": True})


# ---------------------------------------------------------------- generator (gated)
@app.get("/generate", response_class=HTMLResponse)
def generate_form(request: Request):
    user = _user(request)
    if user is None:
        return RedirectResponse("/login", status_code=303)
    if not store.is_subscribed(user["id"]):
        return RedirectResponse("/pricing", status_code=303)
    return templates.TemplateResponse(request, "generate.html", {"user": user})


def _parse_generate_form(form) -> dict:
    juris = set(form.getlist("jurisdictions"))
    data_collected = [s.strip() for s in form.get("data_collected", "").split(",") if s.strip()]
    if not data_collected:
        data_collected = ["Email address", "Usage data"]
    return {
        "business_name": form.get("business_name", "").strip() or "Your Business",
        "website": form.get("website", "").strip() or "https://example.com",
        "contact_email": form.get("contact_email", "").strip() or "privacy@example.com",
        "jurisdictions": juris or {"us"},
        "data_collected": data_collected,
        "uses_cookies": form.get("uses_cookies") == "yes",
        "uses_ai": form.get("uses_ai") == "yes",
    }


@app.post("/generate")
async def generate_run(request: Request):
    user = _user(request)
    if user is None:
        return RedirectResponse("/login", status_code=303)
    if not store.is_subscribed(user["id"]):
        return RedirectResponse("/pricing", status_code=303)
    form = await request.form()
    inputs = _parse_generate_form(form)
    docs = generate_documents(inputs)
    # jurisdictions is a set -> make JSON-serializable
    saved_inputs = dict(inputs)
    saved_inputs["jurisdictions"] = sorted(inputs["jurisdictions"])
    pid = store.save_policy(inputs["business_name"], CLAUSE_LIBRARY_VERSION, saved_inputs, docs)
    return RedirectResponse(f"/p/{pid}", status_code=303)


@app.get("/p/{pid}", response_class=HTMLResponse)
def hosted_bundle(request: Request, pid: str):
    policy = store.get_policy(pid)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return templates.TemplateResponse(request, "hosted.html", {
        "policy": policy, "disclaimer": DISCLAIMER,
        "changelog": CLAUSE_CHANGELOG,
        "documents": policy["docs"],
    })


@app.get("/p/{pid}/{doc}", response_class=HTMLResponse)
def hosted_doc(request: Request, pid: str, doc: str):
    policy = store.get_policy(pid)
    if not policy or doc not in policy["docs"]:
        raise HTTPException(status_code=404, detail="Document not found")
    d = policy["docs"][doc]
    return templates.TemplateResponse(request, "doc.html", {
        "policy": policy, "doc": d, "doc_key": doc,
        "disclaimer": DISCLAIMER,
    })


# ---------------------------------------------------------------- JSON API (for tests/automation)
@app.get("/api/health")
def health():
    return {"status": "ok", "clause_version": CLAUSE_LIBRARY_VERSION,
            "stripe_enabled": auth.stripe_enabled()}


@app.post("/api/scan")
async def api_scan(payload: dict):
    text = payload.get("text", "")
    url = payload.get("url", "")
    if url and not text:
        try:
            text = await _fetch_url_text(url)
        except Exception as e:
            return JSONResponse({"error": f"fetch failed: {e}"}, status_code=400)
    if not text:
        return JSONResponse({"error": "provide 'text' or 'url'"}, status_code=400)
    return scan_text(text)
