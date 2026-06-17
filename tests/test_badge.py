def test_badge_svg_serves_watermarked_sample(client):
    """Public /badge.svg only ever serves a SAMPLE — it must not mint a
    verified-looking badge from an arbitrary score."""
    resp = client.get("/badge.svg?score=999")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("image/svg+xml")
    body = resp.text
    assert "100 out of 100" in body  # score still clamps 0-100
    assert "Grade A" in body
    assert "SAMPLE" in body  # watermarked, not presented as verified
    assert "Verified" not in body


def test_badge_education_page_shows_scale_not_embed(client):
    """The /badge page is educational: grading scale + sample, NO copyable
    real embed code that bypasses scanning."""
    resp = client.get("/badge")
    assert resp.status_code == 200
    text = resp.text
    # grading scale present
    assert "grading scale" in text.lower()
    assert "AI-disclosure" in text
    # explains the verified/anti-forgery value
    assert "verified" in text.lower()
    # must NOT hand out a ready real embed snippet on the public page
    assert "/badge.svg?score=" not in text or "sample=1" in text


def test_verified_badge_is_unforgeable(client):
    """A verified badge must come from a stored scan id, not a URL score.
    Unknown ids must NOT render a real score."""
    # mint from a real scan result
    resp = client.post("/badge/mint", data={"score": "73", "source": "example.com"})
    assert resp.status_code == 200
    assert "grade B" in resp.text  # rendered in the minted-page copy
    assert "73/100" in resp.text
    # extract the verification id from the embed code
    import re
    m = re.search(r"/badge/v/([\w-]+)\.svg", resp.text)
    assert m, "minted page should contain a verified badge URL"
    bid = m.group(1)

    # the verified badge renders the real, stored score
    v = client.get(f"/badge/v/{bid}.svg")
    assert v.status_code == 200
    assert "73 out of 100" in v.text
    assert "Verified" in v.text
    assert "SAMPLE" not in v.text

    # an unknown id must NOT mint a fake score (404 + sample/unverified)
    bad = client.get("/badge/v/totallyfakeid.svg")
    assert bad.status_code == 404
    assert "SAMPLE" in bad.text
