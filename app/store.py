"""SQLite persistence for ClauseKeeper: generated policy bundles + multi-tenant user accounts.

Subscription state is now PER-USER (a real `users` table), not a single global flag.
The old single-row `account` table is left intact for backward compatibility but is no
longer the source of truth for gating.
"""
import json
import os
import secrets
import sqlite3
from datetime import datetime

# Canonical env var is CLAUSEKEEPER_DB; fall back to the legacy POLICYFRESH_DB so
# existing deployments keep working, then to a local clausekeeper.db default.
DB_PATH = (
    os.environ.get("CLAUSEKEEPER_DB")
    or os.environ.get("POLICYFRESH_DB")
    or os.path.join(os.path.dirname(__file__), "..", "clausekeeper.db")
)


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS policies (
                id TEXT PRIMARY KEY,
                business_name TEXT,
                created_at TEXT,
                clause_version TEXT,
                inputs_json TEXT,
                docs_json TEXT
            )
        """)
        # Legacy single-row table — kept so old DBs don't error; not used for gating.
        c.execute("""
            CREATE TABLE IF NOT EXISTS account (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                subscribed INTEGER DEFAULT 0,
                plan TEXT
            )
        """)
        c.execute("INSERT OR IGNORE INTO account (id, subscribed, plan) VALUES (1, 0, NULL)")
        # Real multi-tenant users.
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                stripe_customer_id TEXT,
                subscribed INTEGER DEFAULT 0,
                plan TEXT,
                created_at TEXT
            )
        """)


# ---------------------------------------------------------------- users
def _now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _row_to_user(row):
    if not row:
        return None
    return {
        "id": row["id"],
        "email": row["email"],
        "stripe_customer_id": row["stripe_customer_id"],
        "subscribed": bool(row["subscribed"]),
        "plan": row["plan"],
        "created_at": row["created_at"],
    }


def get_user(user_id: int):
    with _conn() as c:
        row = c.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return _row_to_user(row)


def get_user_by_email(email: str):
    if not email:
        return None
    with _conn() as c:
        row = c.execute("SELECT * FROM users WHERE email = ?", (email.lower().strip(),)).fetchone()
        return _row_to_user(row)


def get_user_by_customer(stripe_customer_id: str):
    if not stripe_customer_id:
        return None
    with _conn() as c:
        row = c.execute(
            "SELECT * FROM users WHERE stripe_customer_id = ?", (stripe_customer_id,)
        ).fetchone()
        return _row_to_user(row)


def upsert_user(email: str, stripe_customer_id: str = None) -> dict:
    """Create or update a user by email. Returns the user dict. Does not change subscription."""
    email = (email or "").lower().strip()
    if not email:
        raise ValueError("email is required")
    with _conn() as c:
        row = c.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if row:
            if stripe_customer_id and not row["stripe_customer_id"]:
                c.execute(
                    "UPDATE users SET stripe_customer_id = ? WHERE id = ?",
                    (stripe_customer_id, row["id"]),
                )
            row = c.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        else:
            c.execute(
                "INSERT INTO users (email, stripe_customer_id, subscribed, plan, created_at) "
                "VALUES (?, ?, 0, NULL, ?)",
                (email, stripe_customer_id, _now()),
            )
            row = c.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return _row_to_user(row)


def is_subscribed(user_id: int) -> bool:
    """User-scoped subscription check. Returns False for unknown/None users."""
    if not user_id:
        return False
    with _conn() as c:
        row = c.execute("SELECT subscribed FROM users WHERE id = ?", (user_id,)).fetchone()
        return bool(row and row["subscribed"])


def set_subscribed(user_id: int, value: bool, plan: str = "always-current-19"):
    """Flip subscription state for a single user."""
    with _conn() as c:
        c.execute(
            "UPDATE users SET subscribed = ?, plan = ? WHERE id = ?",
            (1 if value else 0, plan if value else None, user_id),
        )


def set_subscribed_by_customer(stripe_customer_id: str, value: bool, plan: str = "always-current-19"):
    """Flip subscription state for a user identified by their Stripe customer id (webhook path)."""
    if not stripe_customer_id:
        return None
    with _conn() as c:
        c.execute(
            "UPDATE users SET subscribed = ?, plan = ? WHERE stripe_customer_id = ?",
            (1 if value else 0, plan if value else None, stripe_customer_id),
        )
        row = c.execute(
            "SELECT * FROM users WHERE stripe_customer_id = ?", (stripe_customer_id,)
        ).fetchone()
        return _row_to_user(row)


# ---------------------------------------------------------------- policies
def save_policy(business_name: str, clause_version: str, inputs: dict, docs: dict) -> str:
    pid = secrets.token_urlsafe(8)
    with _conn() as c:
        c.execute(
            "INSERT INTO policies (id, business_name, created_at, clause_version, inputs_json, docs_json) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (pid, business_name, _now(), clause_version, json.dumps(inputs), json.dumps(docs)),
        )
    return pid


def get_policy(pid: str):
    with _conn() as c:
        row = c.execute("SELECT * FROM policies WHERE id = ?", (pid,)).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "business_name": row["business_name"],
            "created_at": row["created_at"],
            "clause_version": row["clause_version"],
            "inputs": json.loads(row["inputs_json"]),
            "docs": json.loads(row["docs_json"]),
        }


def list_policies(limit: int = 50):
    with _conn() as c:
        rows = c.execute(
            "SELECT id, business_name, created_at, clause_version FROM policies "
            "ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]
