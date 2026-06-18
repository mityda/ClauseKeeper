# Copilot instructions for ClauseKeeper

ClauseKeeper is an AGPL-3.0 open-source FastAPI app for scanning website legal/compliance documents and generating current Privacy Policy, Terms, Cookie Policy, and AI-Disclosure documents. It is an open-core SaaS: the scanner/generator/self-hosted app are free and work with no external keys; the paid cloud tier provides managed hosting, always-current clause maintenance, and optional Stripe billing.

## How to work in this repo

Use the repo root as your working directory.

Preferred setup:

```bash
uv sync --dev
cp .env.example .env
uv run pytest
```

Alternative venv setup:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pytest pytest-asyncio
cp .env.example .env
pytest
```

Run locally:

```bash
uv run uvicorn app.main:app --reload
```

Docker self-host smoke test:

```bash
cp .env.example .env
docker compose up
```

`app/main.py` exposes the FastAPI app as `app.main:app`; there is no separate Python entrypoint script.

## Architecture quick map

- `app/main.py`: routes, Jinja2 pages, scanner/generator endpoints, badges, login/subscription gating, Stripe Checkout/Portal/webhooks, health checks.
- `app/auth.py`: signed session cookie helpers and Stripe-enabled detection. Treat as security-sensitive.
- `app/store.py`: SQLite users, subscriptions, generated policy bundles, verified badges.
- `app/generator.py`: deterministic document generator plus clause library version/changelog/disclaimer.
- `app/scanner.py`: deterministic rule engine that evaluates normalized text against rules.
- `app/clause_rules.py`: weighted clause-rule configuration and core scanner IP.
- `templates/`, `static/style.css`: server-rendered UI, vanilla CSS.
- `tests/`: pytest suite; expected full run is 31 tests passing.

## Non-negotiable product constraints

- Core scanner/generator must remain deterministic, auditable, and cheap to run.
- **Do not add an LLM dependency to the core product.** No required OpenAI/Anthropic/etc. calls in scanner, generator, tests, or self-host path.
- Keep self-hosting working with no Stripe keys, no paid APIs, and no secrets.
- Use FastAPI + Jinja2 + vanilla HTML/CSS. Do not introduce a JS framework for ordinary UI changes.

## Security and privacy expectations

ClauseKeeper handles legal-document content and billing state. Do not log or commit real customer documents, `.env`, SQLite DBs, API keys, or Stripe secrets. Preserve signed-cookie security settings in `app/auth.py`. Preserve Stripe webhook signature verification in `app/main.py`.

Generated documents must keep a clear “not legal advice” disclaimer, a visible last-updated date, and the `CLAUSE_LIBRARY_VERSION` stamp. If touching generation or hosted document display, verify these still render.

## What a good PR looks like

- Small, focused change with a clear reason.
- Tests added/updated for behavior changes, especially scanner rules and generator output.
- `uv run pytest` (or `pytest` in venv) passes from repo root.
- No core LLM dependency or required external service added.
- Open-core boundary respected: free/self-host features still work without cloud-only services.
- Docs/instructions updated when commands, behavior, or deployment assumptions change.
