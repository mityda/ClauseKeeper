"""Privacy-friendly first-party analytics for ClauseKeeper.

Server-side only: no cookies, no client JavaScript tracker, and no raw IP/User-Agent
storage. Visitors are represented by a daily rotating hash derived from IP + UA +
date so launch-day funnels can be measured without building profiles.
"""
import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Request

from . import store


_PERIODS = {
    "last_24h": "Last 24 hours",
    "last_7d": "Last 7 days",
    "all_time": "All time",
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _day(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).date().isoformat()


def init_db() -> None:
    """Create the analytics table and indexes in the shared ClauseKeeper DB."""
    with store._conn() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event TEXT NOT NULL,
                path TEXT,
                ts TEXT NOT NULL,
                day TEXT NOT NULL,
                visitor TEXT NOT NULL,
                meta TEXT
            )
            """
        )
        c.execute("CREATE INDEX IF NOT EXISTS idx_events_event_day ON events (event, day)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_events_ts ON events (ts)")


def visitor_hash(request: Request, day: str | None = None) -> str:
    """Return an anonymous daily visitor hash. Does not expose raw IP or UA."""
    day = day or _day(_now())
    forwarded_for = request.headers.get("x-forwarded-for", "")
    ip = forwarded_for.split(",", 1)[0].strip()
    if not ip and request.client:
        ip = request.client.host or ""
    ua = request.headers.get("user-agent", "")
    digest = hashlib.sha256(f"ck-v1|{day}|{ip}|{ua}".encode("utf-8")).hexdigest()
    return digest


def record_event(request: Request, event: str, meta: dict[str, Any] | None = None) -> None:
    """Insert an analytics event. Fail silently; never break the request path."""
    try:
        init_db()
        now = _now()
        day = _day(now)
        meta_json = json.dumps(meta, sort_keys=True, separators=(",", ":")) if meta else None
        with store._conn() as c:
            c.execute(
                "INSERT INTO events (event, path, ts, day, visitor, meta) VALUES (?, ?, ?, ?, ?, ?)",
                (event, str(request.url.path), _iso(now), day, visitor_hash(request, day), meta_json),
            )
    except Exception:
        return None


def _percent(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round((numerator / denominator) * 100, 1)


def _period_where(period: str) -> tuple[str, tuple[Any, ...]]:
    now = _now()
    if period == "last_24h":
        return "ts >= ?", (_iso(now - timedelta(hours=24)),)
    if period == "last_7d":
        return "day >= ?", (_day(now - timedelta(days=7)),)
    return "1=1", ()


def _count(c, where: str, params: tuple[Any, ...], extra: str = "") -> int:
    row = c.execute(f"SELECT COUNT(*) AS ct FROM events WHERE {where} {extra}", params).fetchone()
    return int(row["ct"] if row else 0)


def _unique(c, where: str, params: tuple[Any, ...]) -> int:
    row = c.execute(f"SELECT COUNT(DISTINCT visitor) AS ct FROM events WHERE {where}", params).fetchone()
    return int(row["ct"] if row else 0)


def stats_summary() -> dict[str, Any]:
    """Return launch funnel metrics for the admin stats views."""
    init_db()
    periods: dict[str, Any] = {}
    with store._conn() as c:
        for key, label in _PERIODS.items():
            where, params = _period_where(key)
            page_views = _count(c, where, params, "AND event = 'page_view'")
            pricing_views = _count(c, where, params, "AND event = 'page_view' AND path = '/pricing'")
            scans = _count(c, where, params, "AND event = 'scan_completed'")
            checkouts = _count(c, where, params, "AND event = 'checkout_started'")
            periods[key] = {
                "label": label,
                "page_views": page_views,
                "unique_visitors": _unique(c, where, params),
                "scans_completed": scans,
                "checkouts_started": checkouts,
                "funnel": {
                    "scan_completed": scans,
                    "pricing_page_views": pricing_views,
                    "checkout_started": checkouts,
                    "pricing_from_scan_pct": _percent(pricing_views, scans),
                    "checkout_from_pricing_pct": _percent(checkouts, pricing_views),
                    "checkout_from_scan_pct": _percent(checkouts, scans),
                },
            }
    return {"periods": periods}
