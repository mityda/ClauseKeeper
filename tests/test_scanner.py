"""(a) The free scanner still works."""
from app.scanner import scan_text, html_to_text


def test_scan_text_returns_scorecard():
    result = scan_text("We collect your email address. You can request deletion. GDPR.")
    assert "score_100" in result
    assert 0 <= result["score_100"] <= 100
    assert "grade" in result
    assert result["counts"]["total"] > 0
    assert isinstance(result["results"], list)


def test_scan_empty_text_is_low_score():
    result = scan_text("")
    assert result["score_100"] == 0
    assert result["grade"] == "F"


def test_html_to_text_strips_tags_and_scripts():
    txt = html_to_text("<html><body><p>Hello</p><script>bad()</script></body></html>")
    assert "Hello" in txt
    assert "bad()" not in txt


def test_api_scan_endpoint(client):
    resp = client.post("/api/scan", json={"text": "We use cookies and collect personal data."})
    assert resp.status_code == 200
    assert "score_100" in resp.json()


def test_health_endpoint(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["stripe_enabled"] is False
