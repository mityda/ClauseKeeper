"""ClauseKeeper MCP server.

Exposes the deterministic ClauseKeeper compliance scanner as Model Context
Protocol tools. This module intentionally keeps wrappers thin and delegates all
scoring to app.scanner.scan_text.
"""
from __future__ import annotations

import re
import sys
import urllib.request
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# Allow this standalone MCP package (repo/mcp/server.py) to import the parent
# ClauseKeeper app package without requiring the main app to be installed.
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from app.clause_rules import CLAUSE_RULES, MAX_RAW_SCORE  # noqa: E402
from app.scanner import html_to_text, scan_text  # noqa: E402

USER_AGENT = "ClauseKeeperMCP/0.1 (+https://github.com/)"
MAX_FETCH_BYTES = 2_000_000

mcp = FastMCP(
    "clausekeeper-mcp",
    instructions=(
        "Use these tools to scan privacy policies, terms, cookie policies, "
        "and related compliance documents with ClauseKeeper's deterministic "
        "rule-based scanner. No LLM or API key is used."
    ),
)


def _checklist(result: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the missing/stale clause checklist from a scanner scorecard."""
    return [
        {
            "key": item["key"],
            "label": item["label"],
            "category": item["category"],
            "status": item["status"],
            "weight": item["weight"],
            "earned": item["earned"],
            "why": item["why"],
            "fix": item["fix"],
        }
        for item in result.get("missing_or_stale", [])
    ]


def _scan_response(raw_text: str, *, source: str) -> dict[str, Any]:
    """Run the real scanner and shape a compact agent-facing response."""
    result = scan_text(raw_text)
    return {
        "source": source,
        "score_100": result["score_100"],
        "score_10": result["score_10"],
        "grade": result["grade"],
        "verdict": result["verdict"],
        "word_count": result["word_count"],
        "counts": result["counts"],
        "missing_or_stale": _checklist(result),
        "by_category": result["by_category"],
    }


def _fetch_url_text(url: str) -> str:
    """Fetch visible text from a policy URL using stdlib urllib + scanner HTML strip."""
    clean_url = (url or "").strip()
    if not clean_url:
        raise ValueError("url is required")
    if not clean_url.startswith(("http://", "https://")):
        clean_url = "https://" + clean_url

    request = urllib.request.Request(clean_url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=15) as response:  # noqa: S310 - user-requested scan URL
        content_type = response.headers.get("Content-Type", "")
        charset_match = re.search(r"charset=([^;]+)", content_type, re.I)
        charset = charset_match.group(1).strip() if charset_match else "utf-8"
        raw = response.read(MAX_FETCH_BYTES + 1)
        if len(raw) > MAX_FETCH_BYTES:
            raise ValueError(f"URL response exceeds {MAX_FETCH_BYTES} byte limit")
        html = raw.decode(charset, errors="replace")
    return html_to_text(html)


@mcp.tool()
def scan_policy_text(text: str) -> dict[str, Any]:
    """Scan pasted policy text and return score plus missing/stale clause checklist."""
    return _scan_response(text or "", source="pasted text")


@mcp.tool()
def scan_policy_url(url: str) -> dict[str, Any]:
    """Fetch a policy URL, strip HTML, and scan its visible text."""
    return _scan_response(_fetch_url_text(url), source=url)


@mcp.tool()
def list_clause_rules() -> dict[str, Any]:
    """List the ClauseKeeper rules/categories used by the scanner."""
    categories: dict[str, int] = {}
    for rule in CLAUSE_RULES:
        categories[rule["category"]] = categories.get(rule["category"], 0) + 1
    return {
        "total_rules": len(CLAUSE_RULES),
        "max_raw_score": MAX_RAW_SCORE,
        "categories": categories,
        "rules": [dict(rule) for rule in CLAUSE_RULES],
    }


def main() -> None:
    """Run the MCP server over stdio transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
