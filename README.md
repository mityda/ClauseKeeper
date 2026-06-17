# ClauseKeeper

**Always-current legal & AI-disclosure documents for indie online businesses.**
Generate a Privacy Policy, Terms of Service, Cookie Policy, and a 2026 AI-Disclosure
addendum in two minutes — and use a free compliance scanner as the lead magnet.

> One-liner: *"Is your privacy policy 2026-compliant?"* — scan it free, then get
> always-current docs for $19/mo.

This is the #1 vetted micro-SaaS idea from `../saas-opportunities/SHORTLIST.md`
(low build effort, recurring revenue, near-zero infra, defensible wedge = the
regulatory churn of 2026: EU AI Act phases + US state AI/privacy laws).

---

## What it is (MVP scope)

1. **Free Compliance Scanner (the wedge).** Paste your policy text OR a URL. The
   tool fetches/scans the text and returns a 0–100 (and 0–10) scorecard flagging
   each clause as **present / needs-update (stale) / missing**: GDPR, CCPA/CPRA,
   cookie consent, data retention, **AI disclosure (the 2026 wedge)**, automated
   decision-making, contact/DPO, COPPA/children, third-party sharing, international
   transfers, and a last-updated stamp. 100% rule-based — **$0 to run, no LLM**.

2. **Policy Doc Generator (the paid product).** A guided form (business, website,
   jurisdictions, data collected, cookies y/n, AI y/n, contact email) assembles
   four documents from templates with **conditional clauses** (GDPR section only if
   EU/UK, CCPA only if US/CA, cookie/AI sections toggled, SCC transfer section only
   if EU/UK). Every doc carries a **"not legal advice" disclaimer**, a **last-updated
   date**, and a **clause-library version stamp** + changelog.

3. **Hosted policy URLs.** Each generated set is persisted to SQLite and served at a
   stable slug: `/p/<id>` (bundle) and `/p/<id>/<doc>` (privacy|terms|cookies|ai).

4. **Pricing / paywall (STUBBED).** Scanner is free + unlimited. Generation is gated
   behind a $19/mo "Always-Current" plan. **Payment is stubbed** — the Subscribe
   button flips a local flag. The real Stripe integration point is clearly marked in
   `app/main.py` (`/subscribe`), with env vars in `.env.example`. **No real keys.**

---

## How to run

Requires [uv](https://docs.astral.sh/uv/) (already installed on this machine) and
Python 3.11.

```bash
cd /Users/michaeldade.oc/projects/clausekeeper
./run.sh
# or directly:
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Then open http://127.0.0.1:8000

Dependencies (installed via `uv add`): fastapi, uvicorn[standard], jinja2,
python-multipart, httpx.

### SEO content drafts

ClauseKeeper has a zero-token content draft generator for long-tail compliance search queries:

```bash
python3 scripts/generate_seo_draft.py --list
python3 scripts/generate_seo_draft.py          # writes the next unbuilt draft to content/drafts/
```

Drafts include front matter, target keyword, free-scanner CTA, FAQ copy, and JSON-LD FAQ schema for review before publication.

### Quick smoke test (curl)

```bash
# health
curl -s http://127.0.0.1:8000/api/health

# scan pasted text
curl -s -X POST http://127.0.0.1:8000/api/scan -H 'Content-Type: application/json' \
  -d '{"text":"We collect email and use cookies. Contact hi@example.com."}'

# scan a URL (fetch + scan)
curl -s -X POST http://127.0.0.1:8000/api/scan -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com/privacy"}'

# subscribe (stub) then generate
curl -s -X POST http://127.0.0.1:8000/subscribe
curl -si -X POST http://127.0.0.1:8000/generate \
  --data-urlencode "business_name=Acme AI Apps LLC" \
  --data-urlencode "website=https://acme.app" \
  --data-urlencode "contact_email=privacy@acme.app" \
  --data-urlencode "jurisdictions=eu" --data-urlencode "jurisdictions=ca" \
  --data-urlencode "uses_cookies=yes" --data-urlencode "uses_ai=yes"
# -> 303 redirect to /p/<id>  (open that URL to see the hosted docs)
```

---

## Architecture

```
clausekeeper/
├── app/
│   ├── main.py          FastAPI app: routes, URL fetch, JSON API, Stripe stub
│   ├── scanner.py       Rule-based scanner engine + HTML-to-text extractor
│   ├── clause_rules.py  ★ The clause-rules config (edit THIS to tune the scanner)
│   ├── generator.py     Template-based doc builder w/ conditional clauses + versioning
│   └── store.py         SQLite persistence (policies + stubbed subscription flag)
├── templates/           Jinja2 server-rendered HTML (base, landing, scan, pricing,
│                        generate, hosted, doc)
├── static/style.css     Styling
├── run.sh               Launch script
├── .env.example         Stripe + app config placeholders (NO real keys)
└── clausekeeper.db       SQLite (auto-created on first run)
```

**Stack:** FastAPI + Jinja2 server-rendered HTML + a little vanilla form JS. No build
step, minimal deps, instant to run/test. SQLite for persistence (swap for Postgres in
prod by changing `store.py`).

### The clause-rules system (`app/clause_rules.py`)

The scanner is a generic engine driven entirely by a list of declarative rules. Each
rule has:

- `signals` — phrases whose presence means the clause **exists**.
- `stale_signals` (optional) — modern-language markers; if the clause exists but none
  of these appear, it's flagged **needs-update / stale** (partial credit). This is how
  we detect, e.g., an old CCPA reference that predates CPRA's "do not sell **or share**."
- `weight` — points toward the /100 score.
- `why` / `fix` — user-facing explanation and remediation tip.

To support a new law, **add one dict to `CLAUSE_RULES`** — no engine changes. To keep
generated docs current, bump `CLAUSE_LIBRARY_VERSION` and add a `CLAUSE_CHANGELOG`
entry in `generator.py`; that version stamp is what justifies the recurring fee.

---

## ⚠️ Honest limitations

- **Generated documents are template-based**, not bespoke legal drafting. They are a
  strong, current starting point — **not a substitute for a lawyer**. Every doc says
  so. Get a legal review before relying on them in production.
- The scanner uses **keyword/heuristic** detection, not legal reasoning. It reliably
  catches missing/stale *language*, but a clause could be present yet legally
  insufficient. It's a lead-gen/triage tool, framed as such.
- Payments are **stubbed**. No money moves until Stripe is wired in.

---

## WHAT MASTER MIKE MUST PROVIDE TO GO LIVE

1. **Domain name** — e.g. `clausekeeper.com` (or chosen name; "ClauseKeeper" is a
   working title — check trademark availability vs. Termly/iubenda/Termageddon).
2. **Stripe account + API keys** — create a $19/mo recurring Price, then fill
   `.env`: `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_PRICE_ID`,
   `STRIPE_WEBHOOK_SECRET`. Wire the marked integration point in `app/main.py`
   (`/subscribe` → Checkout Session) and add a webhook handler that calls
   `store.set_subscribed(True)` on `checkout.session.completed` / `invoice.paid`.
   (Also add real user accounts/auth — the MVP uses a single global subscription
   flag for demo purposes.)
3. **A hosting / deploy target** — e.g. Fly.io, Render, Railway, or a small VPS.
   Move SQLite → managed Postgres for multi-instance hosting (change `store.py`).
   Put it behind HTTPS.
4. **A legal review** — have a qualified attorney review the clause templates and the
   scanner's claims for each target jurisdiction before marketing them. Keep the
   "not legal advice" disclaimer. Consider professional liability insurance.
5. **(Recommended) A clause-update process** — the whole pitch is "always-current."
   Set a cadence (or alerts) to update `CLAUSE_RULES` / templates as laws change, bump
   `CLAUSE_LIBRARY_VERSION`, and notify subscribers. That's the recurring value.
6. **(Optional) Real user auth + multi-tenant accounts**, email (for the scanner lead
   capture + update notifications), and analytics.
```

*Status: local MVP. Runs and is tested end-to-end on this machine. NOT deployed.*
