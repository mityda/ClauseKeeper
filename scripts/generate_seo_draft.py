#!/usr/bin/env python3
"""Generate zero-token SEO draft articles for ClauseKeeper.

This is intentionally deterministic and stdlib-only: it turns a curated backlog of
long-tail compliance queries into review-ready Markdown drafts under content/drafts.
No paid APIs, no network calls, no production writes.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "content" / "drafts"


@dataclass(frozen=True)
class Topic:
    slug: str
    keyword: str
    title: str
    audience: str
    pain: str
    angle: str
    checklist: tuple[str, ...]
    faqs: tuple[tuple[str, str], ...]


TOPICS: tuple[Topic, ...] = (
    Topic(
        slug="is-my-privacy-policy-2026-compliant",
        keyword="is my privacy policy 2026 compliant",
        title="Is My Privacy Policy 2026-Compliant? A Practical Checklist for Online Businesses",
        audience="indie SaaS founders, ecommerce operators, newsletter businesses, and AI app builders",
        pain="Privacy, cookie, AI-disclosure, and state-law language can go stale quietly while the business keeps shipping.",
        angle="Use a plain-English gap check before you pay for legal review or paste another outdated template into production.",
        checklist=(
            "A clear last-updated date that matches the current policy version.",
            "What personal data you collect, including analytics, support, payments, and account data.",
            "Why you collect it: service delivery, security, marketing, legal obligations, and product improvement.",
            "Cookie and tracking disclosures, plus how visitors can change choices where required.",
            "GDPR-style rights language for access, deletion, correction, portability, objection, and consent withdrawal.",
            "CCPA/CPRA-style rights language for California users, including opt-out language for selling or sharing data when relevant.",
            "AI disclosure if your product uses automated generation, recommendations, scoring, or decision support.",
            "Data retention rules that say how long records are kept and what triggers deletion.",
            "Third-party processor categories such as hosting, payments, analytics, email, support, and fraud prevention.",
            "International transfer language if users, vendors, or infrastructure cross borders.",
        ),
        faqs=(
            ("Do I need a lawyer to update my privacy policy?", "A lawyer is the safest final reviewer, but a structured scan helps you identify obvious gaps before review."),
            ("How often should I update my privacy policy?", "Review it any time your data practices change and at least quarterly if you use AI tools, ad pixels, analytics, or new vendors."),
            ("Is a free template enough?", "A template is a starting point. It becomes risky when it does not match your actual product, data flows, jurisdictions, or AI use."),
        ),
    ),
    Topic(
        slug="privacy-policy-ai-disclosure-examples",
        keyword="privacy policy AI disclosure examples",
        title="Privacy Policy AI Disclosure Examples for SaaS and Online Businesses",
        audience="businesses adding AI features to products, support, marketing, or internal workflows",
        pain="Customers increasingly expect to know when data touches automated systems, but many policies still ignore AI entirely.",
        angle="Add AI language that is specific enough to build trust without overclaiming legal certainty.",
        checklist=(
            "State whether AI is used for content generation, recommendations, classification, fraud prevention, support, or analytics.",
            "Explain what categories of user data may be processed by AI-assisted systems.",
            "Say whether humans review important outputs or decisions.",
            "Name the vendor categories involved, such as AI infrastructure providers or model APIs, when applicable.",
            "Avoid promising that AI is never used unless you have verified every workflow and vendor.",
            "Explain how users can contact you about AI-related privacy questions.",
        ),
        faqs=(
            ("Should my privacy policy name every AI vendor?", "It depends on your legal posture and vendor contracts, but listing vendor categories is usually better than staying silent."),
            ("Do internal AI tools count?", "They can. If customer or user data is processed through internal AI workflows, disclose the practice clearly."),
            ("Can ClauseKeeper write the final legal language?", "ClauseKeeper generates template-based starting points and should be reviewed by qualified counsel before production use."),
        ),
    ),
    Topic(
        slug="ccpa-cpra-do-not-sell-or-share-checklist",
        keyword="CCPA CPRA do not sell or share checklist",
        title="CCPA/CPRA “Do Not Sell or Share” Checklist for Small Online Businesses",
        audience="US online businesses with California visitors, customers, analytics, ad pixels, or marketing vendors",
        pain="Older policies often say “do not sell” but miss CPRA-style sharing language tied to cross-context behavioral advertising.",
        angle="Check the visible signals that tell California visitors you understand modern opt-out expectations.",
        checklist=(
            "Use “sell or share” language, not just legacy “sell” language, if advertising or tracking vendors are involved.",
            "Explain the categories of personal information collected and disclosed.",
            "Describe consumer rights: access, deletion, correction, portability, opt-out, and limiting sensitive data use where applicable.",
            "Provide a working contact method for privacy requests.",
            "Document response timelines and verification requirements.",
            "Review cookie banners, analytics, and ad pixels against the policy language.",
        ),
        faqs=(
            ("Does every small business need a CCPA/CPRA section?", "Not always. But if you serve California users or use ad/analytics tooling, it is worth checking threshold and disclosure obligations."),
            ("What changed with CPRA language?", "The phrase “share” became important for certain advertising and cross-context behavioral uses, even where no money changes hands."),
            ("Can I just copy another company’s California section?", "No. Your policy should match your actual data flows, vendors, and user rights process."),
        ),
    ),
    Topic(
        slug="cookie-policy-requirements-for-saas-websites",
        keyword="cookie policy requirements for SaaS websites",
        title="Cookie Policy Requirements for SaaS Websites: A Founder-Friendly Checklist",
        audience="SaaS founders and operators running analytics, product telemetry, embedded media, support widgets, or ads",
        pain="Cookie language is easy to overlook because it sits between legal, marketing, product, and analytics teams.",
        angle="Map cookies to actual business tools so your policy, banner, and site behavior tell the same story.",
        checklist=(
            "List essential, analytics, preference, support, and advertising cookie categories separately.",
            "Explain what each category does in plain language.",
            "Name important vendors or vendor categories, especially analytics and advertising tools.",
            "Tell visitors how to manage choices through your banner, account settings, browser controls, or contact channel.",
            "Match policy language to actual scripts loaded on the site.",
            "Re-check cookies when marketing adds a new pixel, chat widget, or embedded media tool.",
        ),
        faqs=(
            ("Do SaaS websites need a separate cookie policy?", "Not always, but a separate page or section can make cookie disclosures easier to maintain and scan."),
            ("Are analytics cookies considered essential?", "Usually no. Treat analytics as a separate category unless counsel confirms a narrower approach for your situation."),
            ("What is the fastest first step?", "Inventory the scripts on your site, then compare them to the cookie language users can read."),
        ),
    ),
)


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def draft_path(topic: Topic, output_dir: Path, day: date) -> Path:
    return output_dir / f"{day.isoformat()}-{topic.slug}.md"


def existing_slugs(output_dir: Path) -> set[str]:
    if not output_dir.exists():
        return set()
    slugs: set[str] = set()
    for path in output_dir.glob("*.md"):
        match = re.match(r"\d{4}-\d{2}-\d{2}-(.+)\.md$", path.name)
        if match:
            slugs.add(match.group(1))
    return slugs


def select_topic(topic_key: str, output_dir: Path) -> Topic:
    key = (topic_key or "next").strip().lower()
    if key and key != "next":
        for topic in TOPICS:
            if key in {topic.slug, slugify(topic.keyword), slugify(topic.title)}:
                return topic
        raise SystemExit(f"Unknown topic '{topic_key}'. Run --list to see options.")

    built = existing_slugs(output_dir)
    for topic in TOPICS:
        if topic.slug not in built:
            return topic
    return TOPICS[0]


def render_article(topic: Topic, day: date) -> str:
    description = f"A practical checklist for {topic.audience} asking: {topic.keyword}?"
    checklist_md = "\n".join(f"{i}. {item}" for i, item in enumerate(topic.checklist, start=1))
    faq_md = "\n\n".join(f"### {q}\n{a}" for q, a in topic.faqs)
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in topic.faqs
        ],
    }
    schema_json = json.dumps(schema, indent=2)
    return f"""---
title: "{topic.title}"
slug: "{topic.slug}"
date: "{day.isoformat()}"
status: "draft"
target_keyword: "{topic.keyword}"
meta_description: "{description[:155]}"
cta: "Scan your policy free with ClauseKeeper"
---

# {topic.title}

**Target keyword:** {topic.keyword}  
**Audience:** {topic.audience}

{topic.pain} {topic.angle}

ClauseKeeper is built for a simple recurring question: are the public legal pages on your site keeping up with the way your business actually operates today? Use this draft as review-ready educational content, not legal advice.

## Quick answer

If your policy does not clearly explain your current data collection, cookies, user rights, third-party vendors, retention practices, and AI-assisted processing, it probably needs an update before you rely on it in 2026.

## The practical checklist

{checklist_md}

## What to do when something is missing

1. Capture the gap in plain English.
2. Confirm the real business practice with the person who owns that workflow.
3. Update the policy language so it matches reality.
4. Run a fresh scan after the change.
5. Send the final version to qualified counsel before production use.

## Where ClauseKeeper fits

ClauseKeeper gives founders a fast, low-cost first pass: paste a policy or scan a URL, get a compliance score, see the missing or stale clauses, then generate an always-current document bundle as a starting point for review.

**CTA:** [Scan your policy free](https://clausekeeper.app/scan) and find the gaps before customers, partners, or regulators do.

## FAQ

{faq_md}

```json
{schema_json}
```

---
Editorial note: Verify jurisdiction-specific claims and examples before publishing. ClauseKeeper is not a law firm and does not provide legal advice.
"""


def write_draft(topic: Topic, output_dir: Path, day: date, force: bool = False) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = draft_path(topic, output_dir, day)
    if path.exists() and not force:
        raise SystemExit(f"Refusing to overwrite existing draft: {path} (use --force)")
    path.write_text(render_article(topic, day), encoding="utf-8")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a zero-token ClauseKeeper SEO article draft.")
    parser.add_argument("--topic", default="next", help="Topic slug/keyword/title, or 'next' for first unbuilt topic.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Where Markdown drafts are written.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Draft date, YYYY-MM-DD. Defaults to today.")
    parser.add_argument("--force", action="store_true", help="Overwrite the same date/topic draft if it already exists.")
    parser.add_argument("--list", action="store_true", help="List available topic slugs and exit.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.list:
        for topic in TOPICS:
            print(f"{topic.slug}\t{topic.keyword}")
        return 0

    day = date.fromisoformat(args.date)
    topic = select_topic(args.topic, args.output_dir)
    path = write_draft(topic, args.output_dir, day, args.force)
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
