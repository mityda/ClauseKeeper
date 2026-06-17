# Self-host ClauseKeeper

ClauseKeeper is a FastAPI app for scanning legal/compliance documents and generating baseline policy pages. The self-hosted path is designed to work locally with no Stripe account and no paid API keys.

## What works in free self-hosted mode

- Compliance scanner at `/scan`
- JSON scanner API at `/api/scan`
- Local email login for development/self-hosted use
- Policy/document generator at `/generate`
- SQLite persistence for generated policies and verified scan badges

## What needs cloud/paid keys

- Stripe Checkout subscriptions and Customer Portal
- Stripe webhook subscription syncing
- Hosted/cloud commercial operations such as managed billing and always-current hosted updates

If `STRIPE_SECRET_KEY` is blank or unset, ClauseKeeper boots with `stripe_enabled: false` and keeps the scanner/generator usable for local self-hosting.

## Prerequisites

- Docker and Docker Compose v2
- Git

## Quick start with Docker

1. Clone the repo:

   ```bash
   git clone https://github.com/your-org/clausekeeper.git
   cd clausekeeper
   ```

2. Create your local environment file:

   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and set at least `APP_SECRET_KEY` to a long random value:

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

   For a local-only test run, you can leave all `STRIPE_*` values blank.

4. Start ClauseKeeper:

   ```bash
   docker compose up --build
   ```

5. Open the app:

   - Web app: http://localhost:8000
   - Scanner: http://localhost:8000/scan
   - Health check: http://localhost:8000/health

## Data persistence

`docker-compose.yml` mounts a named Docker volume at `/data` and sets:

```env
CLAUSEKEEPER_DB=/data/clausekeeper.db
```

That keeps the SQLite database outside the container filesystem, so generated policies, users, and badges survive container rebuilds/restarts.

Useful commands:

```bash
# Start in the foreground
docker compose up --build

# Start in the background
docker compose up -d --build

# View logs
docker compose logs -f

# Stop containers but keep the SQLite volume
docker compose down

# Stop and delete persisted local data too
docker compose down -v
```

## Environment variables

See `.env.example` for the complete list read by the app.

Required for normal self-hosting:

- `APP_SECRET_KEY` — signs session cookies; change it for any non-throwaway instance.
- `APP_BASE_URL` — public base URL for redirects/cookie behavior, e.g. `http://localhost:8000`.
- `CLAUSEKEEPER_DB` — SQLite DB path; Docker uses `/data/clausekeeper.db`.
- `PORT` — optional in Docker, defaults to `8000`.

Optional cloud/paid features:

- `STRIPE_SECRET_KEY` — enables real Stripe mode when set.
- `STRIPE_PRICE_ID_MONTHLY`, `STRIPE_PRICE_ID_ANNUAL` — Stripe subscription price IDs.
- `STRIPE_PRICE_ID` — legacy monthly fallback.
- `STRIPE_WEBHOOK_SECRET` — validates `/webhook/stripe` events.
- `POLICYFRESH_DB` — legacy database path fallback; prefer `CLAUSEKEEPER_DB`.

## Enabling Stripe billing

For local/open-source self-hosting, leave Stripe variables blank. To run a production paid instance:

1. Create Stripe subscription products/prices.
2. Set `STRIPE_SECRET_KEY`.
3. Set `STRIPE_PRICE_ID_MONTHLY` and/or `STRIPE_PRICE_ID_ANNUAL`.
4. Configure Stripe to send webhooks to `https://your-domain.example/webhook/stripe`.
5. Set `STRIPE_WEBHOOK_SECRET` from the webhook endpoint.
6. Set `APP_BASE_URL` to your public HTTPS URL.

When `STRIPE_SECRET_KEY` is set, `/subscribe` creates real Stripe Checkout Sessions instead of using the local no-Stripe flow.

## Local smoke tests

With the container running:

```bash
curl -i http://localhost:8000/health
curl -I http://localhost:8000/scan
```

Expected health response includes:

```json
{"status":"ok","stripe_enabled":false}
```

The exact `clause_version` value may change as the library evolves.
