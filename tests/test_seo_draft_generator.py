import importlib.util
import sys
from datetime import date
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "generate_seo_draft.py"
spec = importlib.util.spec_from_file_location("generate_seo_draft", MODULE_PATH)
assert spec is not None and spec.loader is not None
seo = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = seo
spec.loader.exec_module(seo)


def test_render_article_contains_seo_metadata_and_cta():
    topic = seo.TOPICS[0]
    article = seo.render_article(topic, date(2026, 6, 17))

    assert 'status: "draft"' in article
    assert f'target_keyword: "{topic.keyword}"' in article
    assert "https://clausekeeper.app/scan" in article
    assert "FAQPage" in article
    assert "not legal advice" in article.lower()


def test_write_draft_selects_next_unbuilt_topic(tmp_path):
    first = seo.select_topic("next", tmp_path)
    path = seo.write_draft(first, tmp_path, date(2026, 6, 17))

    assert path.name == f"2026-06-17-{first.slug}.md"
    assert path.exists()
    assert first.slug in seo.existing_slugs(tmp_path)

    second = seo.select_topic("next", tmp_path)
    assert second.slug != first.slug


def test_topic_lookup_accepts_slug_keyword_or_title(tmp_path):
    topic = seo.TOPICS[1]
    assert seo.select_topic(topic.slug, tmp_path) == topic
    assert seo.select_topic(seo.slugify(topic.keyword), tmp_path) == topic
    assert seo.select_topic(seo.slugify(topic.title), tmp_path) == topic
