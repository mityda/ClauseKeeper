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

## Deploying to Fly.io

Fly.io can deploy this repo directly from the existing `Dockerfile`. Because ClauseKeeper stores its default SQLite database at `/data/clausekeeper.db`, treat the default self-hosted setup as a single-machine app unless you replace SQLite with a networked database.

1. Install `flyctl`, then authenticate:

   ```bash
   fly auth login
   ```

2. From the repository root, create the app config without deploying yet:

   ```bash
   fly launch --no-deploy
   ```

   Accept the Dockerfile-based deploy flow when prompted.

3. Create a persistent volume for the SQLite database in your primary region:

   ```bash
   fly volumes create clausekeeper_data --region <primary-region> --size 1
   ```

4. Update the generated `fly.toml` so the app keeps the same runtime assumptions as `docker-compose.yml`:

   - mount the volume at `/data`
   - set `APP_BASE_URL` to your Fly hostname, for example `https://your-app.fly.dev`
   - set `CLAUSEKEEPER_DB=/data/clausekeeper.db`
   - keep the internal port at `8000`

   Minimal mount block:

   ```toml
   [[mounts]]
     source = "clausekeeper_data"
     destination = "/data"
   ```

5. Set the required secret:

   ```bash
   fly secrets set APP_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
   ```

6. Deploy:

   ```bash
   fly deploy
   ```

7. Verify the running app:

   ```bash
   fly status
   fly logs
   curl -i https://<your-app>.fly.dev/health
   ```

If you later enable billing, add the `STRIPE_*` values with `fly secrets set ...` and redeploy.

## Deploying to Railway

Railway can build this repo from the checked-in `Dockerfile`. The important part is attaching a persistent volume at `/data`, because Railway's default service filesystem is ephemeral across deployments.

1. Push your fork or branch to GitHub.
2. In Railway, create a new project and deploy the GitHub repo.
3. Open the service's Variables tab and add the self-hosting values from `.env.example`:

   - `APP_SECRET_KEY` with a long random value
   - `APP_BASE_URL` with the Railway public domain once it is assigned
   - `CLAUSEKEEPER_DB=/data/clausekeeper.db`
   - `PORT=8000`
   - leave `STRIPE_*` blank unless you are enabling paid billing

4. In the service Settings tab, add a Volume mounted at `/data`.
5. In the service Networking tab, generate a public domain.
6. Add a health check pointing at `/health` so deploys verify the app booted cleanly.
7. Redeploy if Railway does not automatically trigger one after the variable and volume changes.
8. Verify the app:

   ```bash
   curl -i https://<your-railway-domain>/health
   curl -I https://<your-railway-domain>/scan
   ```

As with Fly.io, the default SQLite setup is best kept to a single running instance. If you need horizontal scaling, move persistence off local SQLite first.

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
