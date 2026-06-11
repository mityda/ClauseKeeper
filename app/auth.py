"""Session-cookie auth + Stripe configuration helpers for ClauseKeeper.

Auth model (minimum-viable real, no email infra required):
  - A signed cookie (itsdangerous) carries the logged-in user's id.
  - Subscription is checked per-user against the DB.
  - In Stripe mode, identity is established by verifying a Checkout session
    server-side; in dev/no-Stripe mode, /login accepts an email directly.
"""
import os

from itsdangerous import URLSafeSerializer, BadSignature

from . import store

COOKIE_NAME = "ck_session"

# Dev default keeps local runs working; production MUST set APP_SECRET_KEY.
APP_SECRET_KEY = os.environ.get("APP_SECRET_KEY", "dev-insecure-change-me")
APP_BASE_URL = os.environ.get("APP_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

_serializer = URLSafeSerializer(APP_SECRET_KEY, salt="ck-session")


def stripe_enabled() -> bool:
    return bool(os.environ.get("STRIPE_SECRET_KEY"))


def sign_user_id(user_id: int) -> str:
    return _serializer.dumps({"uid": user_id})


def _unsign(token: str):
    try:
        data = _serializer.loads(token)
        return data.get("uid")
    except (BadSignature, Exception):
        return None


def current_user(request):
    """Return the logged-in user dict from the signed cookie, or None."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    uid = _unsign(token)
    if not uid:
        return None
    return store.get_user(uid)


def set_session_cookie(response, user_id: int):
    secure = APP_BASE_URL.startswith("https://")
    response.set_cookie(
        COOKIE_NAME,
        sign_user_id(user_id),
        httponly=True,
        samesite="lax",
        secure=secure,
        max_age=60 * 60 * 24 * 30,
        path="/",
    )


def clear_session_cookie(response):
    response.delete_cookie(COOKIE_NAME, path="/")
