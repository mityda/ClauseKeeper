"""(d) Webhook handler flips per-user subscribed state given a constructed event.

We run in Stripe-enabled mode here (set STRIPE_SECRET_KEY + WEBHOOK_SECRET), but
monkeypatch stripe.Webhook.construct_event so NO real Stripe API call happens.
"""
import os
import importlib
import tempfile

import pytest


@pytest.fixture()
def stripe_client(monkeypatch):
    tmpdir = tempfile.mkdtemp()
    monkeypatch.setenv("CLAUSEKEEPER_DB", os.path.join(tmpdir, "test.db"))
    monkeypatch.delenv("POLICYFRESH_DB", raising=False)
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_dummy")
    monkeypatch.setenv("STRIPE_PRICE_ID", "price_dummy")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_dummy")
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
        c.ck_store = store
        c.ck_main = main
        yield c


def _post_event(client, event, monkeypatch):
    import stripe
    monkeypatch.setattr(stripe.Webhook, "construct_event", lambda payload, sig, secret: event)
    return client.post("/webhook/stripe", content=b"{}",
                       headers={"stripe-signature": "t=1,v1=abc"})


def test_checkout_completed_subscribes_user(stripe_client, monkeypatch):
    store = stripe_client.ck_store
    event = {
        "type": "checkout.session.completed",
        "data": {"object": {
            "customer": "cus_123",
            "customer_details": {"email": "newcustomer@example.com"},
        }},
    }
    resp = _post_event(stripe_client, event, monkeypatch)
    assert resp.status_code == 200
    user = store.get_user_by_email("newcustomer@example.com")
    assert user is not None
    assert user["subscribed"] is True
    assert user["stripe_customer_id"] == "cus_123"


def test_invoice_paid_resubscribes_by_customer(stripe_client, monkeypatch):
    store = stripe_client.ck_store
    user = store.upsert_user("renewer@example.com", "cus_renew")
    store.set_subscribed(user["id"], False)

    event = {"type": "invoice.paid", "data": {"object": {"customer": "cus_renew"}}}
    resp = _post_event(stripe_client, event, monkeypatch)
    assert resp.status_code == 200
    assert store.get_user(user["id"])["subscribed"] is True


def test_subscription_deleted_unsubscribes(stripe_client, monkeypatch):
    store = stripe_client.ck_store
    user = store.upsert_user("churned@example.com", "cus_churn")
    store.set_subscribed(user["id"], True)

    event = {"type": "customer.subscription.deleted",
             "data": {"object": {"customer": "cus_churn"}}}
    resp = _post_event(stripe_client, event, monkeypatch)
    assert resp.status_code == 200
    assert store.get_user(user["id"])["subscribed"] is False


def test_payment_failed_unsubscribes(stripe_client, monkeypatch):
    store = stripe_client.ck_store
    user = store.upsert_user("failed@example.com", "cus_fail")
    store.set_subscribed(user["id"], True)

    event = {"type": "invoice.payment_failed",
             "data": {"object": {"customer": "cus_fail"}}}
    resp = _post_event(stripe_client, event, monkeypatch)
    assert resp.status_code == 200
    assert store.get_user(user["id"])["subscribed"] is False


def test_bad_signature_returns_400(stripe_client, monkeypatch):
    import stripe

    def _raise(payload, sig, secret):
        raise ValueError("bad signature")

    monkeypatch.setattr(stripe.Webhook, "construct_event", _raise)
    resp = stripe_client.post("/webhook/stripe", content=b"{}",
                              headers={"stripe-signature": "bad"})
    assert resp.status_code == 400
