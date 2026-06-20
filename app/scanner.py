"""
ClauseKeeper compliance scanner engine.

Pure, rule-based ($0 to run). Takes raw policy text (pasted or fetched from a URL)
and evaluates it against CLAUSE_RULES, producing a scorecard.

Status per clause:
  present       -> signals found AND (no stale_signals OR a stale_signal found)
  needs_update  -> signals found BUT stale_signals defined and none matched (STALE)
  missing       -> no signals found
"""
import argparse
import json
import re
import sys
from html.parser import HTMLParser

from .clause_rules import CLAUSE_RULES, MAX_RAW_SCORE


class _TextExtractor(HTMLParser):
    """Strip HTML to visible text. Skips script/style content."""

    def __init__(self):
        super().__init__()
        self._chunks = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self._skip = True

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"):
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            self._chunks.append(data)

    def text(self):
        return " ".join(self._chunks)


def html_to_text(html: str) -> str:
    parser = _TextExtractor()
    try:
        parser.feed(html)
    except Exception:
        # Fall back to a crude tag-strip if the parser chokes on malformed HTML.
        return re.sub(r"<[^>]+>", " ", html)
    return parser.text()


def _contains_any(haystack: str, needles) -> bool:
    return any(n in haystack for n in needles)


def scan_text(raw_text: str) -> dict:
    """Run all clause rules against raw policy text. Returns a scorecard dict."""
    # Normalize: lowercase, collapse whitespace. Heuristic signals are lowercase.
    text = re.sub(r"\s+", " ", (raw_text or "")).lower()
    word_count = len(text.split())

    results = []
    raw_score = 0
    present_ct = stale_ct = missing_ct = 0

    for rule in CLAUSE_RULES:
        has_signal = _contains_any(text, rule["signals"])
        stale_signals = rule.get("stale_signals")

        if not has_signal:
            status = "missing"
            earned = 0
            missing_ct += 1
        elif stale_signals and not _contains_any(text, stale_signals):
            # Present but using outdated/incomplete language for 2026.
            status = "needs_update"
            earned = rule["weight"] // 2  # partial credit
            stale_ct += 1
        else:
            status = "present"
            earned = rule["weight"]
            present_ct += 1

        raw_score += earned
        results.append({
            "key": rule["key"],
            "label": rule["label"],
            "category": rule["category"],
            "status": status,
            "weight": rule["weight"],
            "earned": earned,
            "why": rule["why"],
            "fix": rule["fix"],
        })

    score_100 = round((raw_score / MAX_RAW_SCORE) * 100) if MAX_RAW_SCORE else 0
    # 0-10 headline score for the marketing "X/10" framing.
    score_10 = round(score_100 / 10)

    if score_100 >= 85:
        grade, verdict = "A", "Strong — minor freshness checks only."
    elif score_100 >= 70:
        grade, verdict = "B", "Decent, but missing some 2026-critical clauses."
    elif score_100 >= 50:
        grade, verdict = "C", "Notable gaps — likely not fully 2026-compliant."
    elif score_100 >= 30:
        grade, verdict = "D", "Major gaps. High exposure on privacy/AI rules."
    else:
        grade, verdict = "F", "Little to no compliant policy language detected."

    # Group results by category for display.
    by_category = {}
    for r in results:
        by_category.setdefault(r["category"], []).append(r)

    return {
        "score_100": score_100,
        "score_10": score_10,
        "grade": grade,
        "verdict": verdict,
        "word_count": word_count,
        "counts": {
            "present": present_ct,
            "needs_update": stale_ct,
            "missing": missing_ct,
            "total": len(CLAUSE_RULES),
        },
        "results": results,
        "by_category": by_category,
        "missing_or_stale": [r for r in results if r["status"] != "present"],
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the ClauseKeeper scanner on raw policy text.")
    parser.add_argument("text", nargs="?", help="Policy text to scan. If omitted, stdin is used.")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="Print the full scorecard as JSON.")
    return parser


def _read_cli_text(args: argparse.Namespace) -> str:
    if args.text:
        return args.text

    stdin_text = sys.stdin.read()
    if stdin_text.strip():
        return stdin_text

    raise SystemExit("Provide policy text as an argument or via stdin.")


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    result = scan_text(_read_cli_text(args))

    if args.as_json:
        print(json.dumps(result))
        return 0

    print(f"Score: {result['score_100']}/100 (Grade {result['grade']})")
    print(result["verdict"])
    for item in result["missing_or_stale"]:
        print(f"- {item['label']}: {item['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
