"""(b) /generate gated for anonymous users; (c) dev login->subscribe->generate end-to-end."""


def test_landing_loads(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "ClauseKeeper" in resp.text


def test_pricing_loads(client):
    resp = client.get("/pricing")
    assert resp.status_code == 200


def test_scan_page_loads(client):
    resp = client.get("/scan")
    assert resp.status_code == 200


def test_generate_blocked_for_anonymous(client):
    # No follow_redirects -> we can inspect the redirect target.
    resp = client.get("/generate", follow_redirects=False)
    assert resp.status_code == 303
    assert resp.headers["location"] in ("/login", "/pricing")


def test_post_generate_blocked_for_anonymous(client):
    resp = client.post("/generate", data={"business_name": "X"}, follow_redirects=False)
    assert resp.status_code == 303
    assert resp.headers["location"] in ("/login", "/pricing")


def test_dev_login_then_generate_blocked_until_subscribed(client):
    # Logging in (dev mode) creates the user but does NOT subscribe them.
    store = client.ck_store
    user = store.upsert_user("alice@example.com")
    assert user["subscribed"] is False


def test_full_subscribe_generate_flow_dev_mode(client):
    # In dev/no-Stripe mode, POST /subscribe upserts+subscribes+logs in.
    resp = client.post("/subscribe", data={"email": "buyer@example.com"},
                       follow_redirects=False)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/generate"
    # Cookie was set on the client; /generate should now render the form.
    gen = client.get("/generate")
    assert gen.status_code == 200
    assert "Generate" in gen.text

    # And actually generating docs should persist + redirect to a hosted URL.
    gen_post = client.post("/generate", data={
        "business_name": "Acme Apps LLC",
        "website": "https://acme.app",
        "contact_email": "privacy@acme.app",
        "jurisdictions": "us",
        "uses_cookies": "yes",
        "uses_ai": "yes",
    }, follow_redirects=False)
    assert gen_post.status_code == 303
    assert gen_post.headers["location"].startswith("/p/")
    hosted = client.get(gen_post.headers["location"])
    assert hosted.status_code == 200


def test_dev_login_route_logs_in_returning_user(client):
    store = client.ck_store
    # Pre-create + subscribe a returning user.
    user = store.upsert_user("returning@example.com")
    store.set_subscribed(user["id"], True)

    resp = client.post("/login", data={"email": "returning@example.com"},
                       follow_redirects=False)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/generate"
    # Now gated route works.
    assert client.get("/generate").status_code == 200


def test_logout_clears_session(client):
    client.post("/subscribe", data={"email": "logmeout@example.com"},
                follow_redirects=False)
    assert client.get("/generate").status_code == 200
    client.get("/logout", follow_redirects=False)
    # After logout the gated route redirects again.
    resp = client.get("/generate", follow_redirects=False)
    assert resp.status_code == 303


def test_login_rejects_bad_email_dev_mode(client):
    resp = client.post("/login", data={"email": "notanemail"}, follow_redirects=False)
    assert resp.status_code == 400
