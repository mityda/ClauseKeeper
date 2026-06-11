"""Tests for annual/monthly subscribe price selection."""
import importlib
import os
import tempfile
from types import SimpleNamespace

import pytest


@pytest.fixture()
def stripe_checkout_client(monkeypatch):
    tmpdir = tempfile.mkdtemp()
    monkeypatch.setenv("CLAUSEKEEPER_DB", os.path.join(tmpdir, "test.db"))
    monkeypatch.delenv("POLICYFRESH_DB", raising=False)
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_dummy")
    monkeypatch.setenv("STRIPE_PRICE_ID_ANNUAL", "price_annual")
    monkeypatch.setenv("STRIPE_PRICE_ID_MONTHLY", "price_monthly")
    monkeypatch.delenv("STRIPE_PRICE_ID", raising=False)
    monkeypatch.setenv("APP_SECRET_KEY", "test-secret")
    monkeypatch.setenv("APP_BASE_URL", "http://testserver")

    import app.store as store
    import app.auth as auth
    import app.main as main
    importlib.reload(store)
    importlib.reload(auth)
    importlib.reload(main)

    from fastapi.testclient import TestClient
    store.init_db()
    with TestClient(main.app) as c:
        yield c


def _capture_checkout(monkeypatch):
    import stripe

    captured = {}

    def fake_create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(url="https://checkout.stripe.test/session")

    monkeypatch.setattr(stripe.checkout.Session, "create", fake_create)
    return captured


def test_subscribe_annual_selects_annual_price(stripe_checkout_client, monkeypatch):
    captured = _capture_checkout(monkeypatch)

    resp = stripe_checkout_client.post(
        "/subscribe",
        data={"email": "annual@example.com", "plan": "annual"},
        follow_redirects=False,
    )

    assert resp.status_code == 303
    assert resp.headers["location"] == "https://checkout.stripe.test/session"
    assert captured["line_items"] == [{"price": "price_annual", "quantity": 1}]


def test_subscribe_monthly_selects_monthly_price(stripe_checkout_client, monkeypatch):
    captured = _capture_checkout(monkeypatch)

    resp = stripe_checkout_client.post(
        "/subscribe",
        data={"email": "monthly@example.com", "plan": "monthly"},
        follow_redirects=False,
    )

    assert resp.status_code == 303
    assert captured["line_items"] == [{"price": "price_monthly", "quantity": 1}]


def test_subscribe_missing_plan_defaults_to_annual(stripe_checkout_client, monkeypatch):
    captured = _capture_checkout(monkeypatch)

    resp = stripe_checkout_client.post(
        "/subscribe",
        data={"email": "default@example.com"},
        follow_redirects=False,
    )

    assert resp.status_code == 303
    assert captured["line_items"] == [{"price": "price_annual", "quantity": 1}]


def test_subscribe_invalid_plan_defaults_to_annual(stripe_checkout_client, monkeypatch):
    captured = _capture_checkout(monkeypatch)

    resp = stripe_checkout_client.post(
        "/subscribe",
        data={"email": "invalid@example.com", "plan": "lifetime"},
        follow_redirects=False,
    )

    assert resp.status_code == 303
    assert captured["line_items"] == [{"price": "price_annual", "quantity": 1}]


def test_dev_mode_subscribe_grants_access_for_any_plan(client):
    for plan in ("annual", "monthly", "not-a-plan"):
        fresh = client.get("/logout", follow_redirects=False)
        assert fresh.status_code == 303

        resp = client.post(
            "/subscribe",
            data={"email": f"{plan.replace('-', '')}@example.com", "plan": plan},
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert resp.headers["location"] == "/generate"
        gen = client.get("/generate")
        assert gen.status_code == 200
        assert "Generate" in gen.text
