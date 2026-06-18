# AGENTS.md — ClauseKeeper agent guide

ClauseKeeper is an open-source FastAPI app that scans legal/compliance documents for stale or missing clauses and generates current website legal documents for small SaaS/indie businesses.

## Open-core boundary

- **Free / self-hosted (AGPL-3.0):** the scanner, rule engine, document generator, hosted policy pages, SQLite persistence, Docker setup, and local no-Stripe development flow. Self-hosting needs **no external API keys**.
- **Paid cloud (clausekeeper.app):** hosted maintenance, recurring always-current clause updates, managed Stripe billing/subscriptions, and operational hosting. Stripe is optional and only activates when `STRIPE_SECRET_KEY` is set.
- Keep self-hosted functionality usable without Stripe, paid APIs, or third-party LLM services.

## Architecture overview

- `app/main.py` — FastAPI application, routes, form handling, Jinja2 rendering, scanner endpoints, badge endpoints, auth/billing flow, Stripe Checkout/Portal/webhook integration, generator gating, hosted policy URLs, and health checks. The app object is `app.main:app`.
- `app/auth.py` — signed session-cookie helpers using `itsdangerous`, current-user lookup, secure cookie settings, and Stripe-enabled detection from environment.
- `app/store.py` — SQLite persistence for users/subscriptions, generated policy bundles, and verified scanner badges. Uses `CLAUSEKEEPER_DB`, then legacy `POLICYFRESH_DB`, then local `clausekeeper.db`.
- `app/generator.py` — deterministic paid-product document generator. Builds Privacy Policy, Terms, Cookie Policy, and AI-Disclosure Addendum from structured inputs. Owns `CLAUSE_LIBRARY_VERSION`, `CLAUSE_CHANGELOG`, and `DISCLAIMER`.
- `app/scanner.py` — deterministic compliance scanner engine. Normalizes text, evaluates every rule in `CLAUSE_RULES`, calculates score/grade/statuses, groups results, and strips HTML via a small parser.
- `app/clause_rules.py` — core rule configuration / scanner IP. Defines weighted heuristic clause rules and `MAX_RAW_SCORE`. The scanner reads this generically.
- `app/__init__.py` — package marker.

Other important areas:

- `templates/` — Jinja2 pages. Keep server-rendered HTML simple.
- `static/style.css` — vanilla CSS; no JS framework.
- `tests/` — pytest suite; currently expected to pass with 31 tests.
- `docs/SELF_HOSTING.md`, `docs/LAUNCH_KIT.md`, `CONTRIBUTING.md` — contributor/self-hosting docs.

## Setup commands

From the repo root (`~/projects/clausekeeper`):

### Option A: uv (preferred)

```bash
uv sync --dev
cp .env.example .env
uv run pytest
```

Run the development server:

```bash
uv run uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000>.

### Option B: pip + venv

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pytest pytest-asyncio
cp .env.example .env
pytest
```

Run the development server:

```bash
uvicorn app.main:app --reload
```

### Docker

```bash
cp .env.example .env
docker compose up
```

Open <http://localhost:8000>. The Docker image runs `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`.

## Coding conventions and product constraints

- Stack: FastAPI + Uvicorn + Jinja2 + SQLite + vanilla CSS/HTML. Avoid adding a JavaScript framework.
- Keep Python straightforward and typed where useful, but do not introduce unnecessary abstractions.
- The clause scanner and generator are intentionally **deterministic and rule/template-based**.
- **Do not add an LLM dependency to the core product.** No OpenAI/Anthropic/etc. calls in scanner, generator, tests, or required self-host path.
- Keep external services optional. The scanner/generator must still work with no Stripe keys and no paid APIs.
- Prefer small, focused PRs with tests for behavior changes.

## Legal-domain requirements

Generated legal documents must always include:

- the `DISCLAIMER` meaning: generated output is informational and **not legal advice**;
- a visible `Last updated` date; and
- the `CLAUSE_LIBRARY_VERSION` version stamp.

If you touch `app/generator.py`, hosted document templates, or any generation/display path, verify these are preserved in rendered output and tests.

## Be careful / do not touch casually

- `app/auth.py` — security-sensitive session signing/cookie behavior. Do not weaken `httponly`, `samesite`, `secure`, or signature validation. Production must use a real `APP_SECRET_KEY`.
- `app/clause_rules.py` — core scanner IP. Rule weights, signals, and stale-signal semantics affect scoring and product value. Change carefully and add/update tests.
- Stripe logic in `app/main.py` (`/subscribe`, `/success`, `/portal`, `/webhook/stripe`) — billing and webhook state transitions are security-sensitive. Keep signature verification and no-Stripe fallback intact.
- Do not commit `.env`, secrets, local SQLite DBs, customer/legal documents, or real user data.

## Clause-rule changes

When adding or changing rules:

- preserve the rule shape: `key`, `label`, `category`, `weight`, `signals`, optional `stale_signals`, `why`, `fix`;
- keep signals lowercase because scanner text is lowercased before matching;
- choose stable keys and avoid renaming existing keys without migration/test updates;
- ensure `MAX_RAW_SCORE = sum(r["weight"] for r in CLAUSE_RULES)` remains correct;
- add or update tests in `tests/test_scanner.py` for expected present/missing/needs_update behavior.

## Validate before PR

Run these before opening a PR:

```bash
uv run pytest
```

If using an activated venv instead of uv:

```bash
pytest
```

For app changes, also smoke-test the server:

```bash
uv run uvicorn app.main:app --reload
# then visit http://127.0.0.1:8000 and/or curl http://127.0.0.1:8000/api/health
```

For Docker/self-hosting changes:

```bash
docker compose up
# then visit http://localhost:8000 or curl http://localhost:8000/api/health
```

Before submitting, confirm:

- tests pass;
- no LLM dependency was added to the core product;
- generated docs still show not-legal-advice disclaimer + last-updated date + clause version;
- self-hosted mode works without external keys;
- AGPL/open-core boundary is respected; and
- docs/instructions were updated if behavior or commands changed.
