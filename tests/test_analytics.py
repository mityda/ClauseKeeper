import json

from starlette.requests import Request


def _request(path="/scan", ip="203.0.113.9", ua="ClauseKeeperTest/1.0"):
    return Request({
        "type": "http",
        "method": "GET",
        "path": path,
        "headers": [(b"user-agent", ua.encode("utf-8"))],
        "client": (ip, 12345),
        "scheme": "http",
        "server": ("testserver", 80),
        "query_string": b"",
    })


def _event_counts(store):
    with store._conn() as c:
        rows = c.execute("SELECT event, COUNT(*) AS ct FROM events GROUP BY event").fetchall()
        return {row["event"]: row["ct"] for row in rows}


def test_record_event_inserts_row_and_anonymizes_daily_visitor(client):
    analytics = client.ck_main.analytics
    request = _request()

    analytics.record_event(request, "page_view", {"source": "test"})
    analytics.record_event(request, "page_view", {"source": "test"})

    with client.ck_store._conn() as c:
        rows = c.execute("SELECT event, path, visitor, meta FROM events ORDER BY id").fetchall()

    assert len(rows) == 2
    assert rows[0]["event"] == "page_view"
    assert rows[0]["path"] == "/scan"
    assert rows[0]["visitor"] == rows[1]["visitor"]
    assert "203.0.113.9" not in rows[0]["visitor"]
    assert "ClauseKeeperTest" not in rows[0]["visitor"]
    assert json.loads(rows[0]["meta"]) == {"source": "test"}


def test_admin_stats_invisible_without_token_and_authorized_with_token(client, monkeypatch):
    monkeypatch.delenv("STATS_TOKEN", raising=False)
    assert client.get("/admin/stats").status_code == 404
    assert client.get("/admin/stats.json").status_code == 404

    monkeypatch.setenv("STATS_TOKEN", "launch-token")
    assert client.get("/admin/stats?token=wrong").status_code == 404

    html = client.get("/admin/stats?token=launch-token")
    assert html.status_code == 200
    assert "ClauseKeeper stats" in html.text

    data = client.get("/admin/stats.json?token=launch-token")
    assert data.status_code == 200
    assert "periods" in data.json()
    assert "last_24h" in data.json()["periods"]


def test_scan_and_checkout_instrumentation_increment_counts(client, monkeypatch):
    monkeypatch.setenv("STATS_TOKEN", "stats")

    scan_resp = client.post(
        "/scan",
        data={"mode": "text", "policy_text": "We collect email addresses. You may request deletion. GDPR."},
    )
    assert scan_resp.status_code == 200

    checkout_resp = client.post(
        "/subscribe",
        data={"email": "buyer@example.com", "plan": "annual"},
        follow_redirects=False,
    )
    assert checkout_resp.status_code == 303

    counts = _event_counts(client.ck_store)
    assert counts["scan_completed"] == 1
    assert counts["checkout_started"] == 1

    stats = client.get("/admin/stats.json?token=stats").json()["periods"]["all_time"]
    assert stats["scans_completed"] == 1
    assert stats["checkouts_started"] == 1


def test_pricing_page_view_is_counted_for_funnel(client, monkeypatch):
    monkeypatch.setenv("STATS_TOKEN", "stats")

    resp = client.get("/pricing")
    assert resp.status_code == 200

    stats = client.get("/admin/stats.json?token=stats").json()["periods"]["all_time"]
    assert stats["page_views"] == 1
    assert stats["funnel"]["pricing_page_views"] == 1
