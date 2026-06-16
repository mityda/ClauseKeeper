def test_badge_svg_renders_clamped_score_and_grade(client):
    resp = client.get("/badge.svg?score=999")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("image/svg+xml")
    body = resp.text
    assert "100 out of 100" in body
    assert "Grade A" in body


def test_badge_builder_includes_embed_code(client):
    resp = client.get("/badge?score=73")
    assert resp.status_code == 200
    assert "Put your compliance score on your site" in resp.text
    assert "https://clausekeeper.app/badge.svg?score=73" in resp.text
    assert "Grade B" in resp.text
