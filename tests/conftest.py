"""Shared pytest fixtures. Forces dev/no-Stripe mode and an isolated temp DB
BEFORE app modules are imported, so nothing touches the real DB or Stripe."""
import os
import importlib
import tempfile

import pytest


@pytest.fixture()
def client(monkeypatch):
    # Isolated DB per test; ensure no Stripe keys leak in from the environment.
    tmpdir = tempfile.mkdtemp()
    db_path = os.path.join(tmpdir, "test.db")
    monkeypatch.setenv("CLAUSEKEEPER_DB", db_path)
    monkeypatch.delenv("POLICYFRESH_DB", raising=False)
    monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)
    monkeypatch.delenv("STRIPE_PRICE_ID", raising=False)
    monkeypatch.delenv("STRIPE_PRICE_ID_MONTHLY", raising=False)
    monkeypatch.delenv("STRIPE_PRICE_ID_ANNUAL", raising=False)
    monkeypatch.delenv("STRIPE_WEBHOOK_SECRET", raising=False)
    monkeypatch.setenv("APP_SECRET_KEY", "test-secret")
    monkeypatch.setenv("APP_BASE_URL", "http://testserver")

    # Re-import modules so they pick up the patched env (module-level DB_PATH etc.).
    import app.store as store
    import app.auth as auth
    import app.main as main
    importlib.reload(store)
    importlib.reload(auth)
    importlib.reload(main)

    from fastapi.testclient import TestClient
    store.init_db()
    with TestClient(main.app) as c:
        c.ck_main = main
        c.ck_store = store
        c.ck_auth = auth
        yield c
