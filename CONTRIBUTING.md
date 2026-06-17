# Contributing to ClauseKeeper

Thanks for helping improve ClauseKeeper. Small fixes, docs improvements, tests, and issue reports are all welcome.

## Development setup

### Option A: uv

```bash
git clone https://github.com/your-org/clausekeeper.git
cd clausekeeper
uv sync --dev
cp .env.example .env
uv run pytest
```

Run the app locally:

```bash
uv run uvicorn app.main:app --reload
```

### Option B: pip + venv

```bash
git clone https://github.com/your-org/clausekeeper.git
cd clausekeeper
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pytest pytest-asyncio
cp .env.example .env
pytest
```

Run the app locally:

```bash
uvicorn app.main:app --reload
```

## Tests

Run the full test suite before opening a PR:

```bash
pytest
```

The suite uses isolated temporary SQLite databases and clears Stripe env vars for no-key local testing.

## Code style

- Keep changes focused and easy to review.
- Prefer clear, typed-ish Python and straightforward FastAPI patterns.
- Add or update tests for behavior changes.
- Do not commit `.env`, SQLite databases, API keys, or real customer data.
- Keep Stripe/cloud features optional so the self-hosted scanner and generator keep working without paid keys.

## Claiming an issue

Comment on the issue with a short note about what you plan to work on. If the issue is already assigned or someone recently commented that they are working on it, coordinate there first.

## Pull requests

Please include:

- What changed and why
- How you tested it, including the exact test command
- Screenshots for user-facing UI changes when helpful
