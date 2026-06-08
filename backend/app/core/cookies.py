"""Cookie helpers for httpOnly auth token cookies.

Both the access_token and refresh_token are stored as httpOnly cookies
that the browser sends automatically on every request. This eliminates
the need for the frontend to manage tokens in localStorage.
"""

from datetime import datetime, timedelta, timezone

from fastapi import Response

from app.config import settings

# ── Cookie names ──────────────────────────────────────────────────

ACCESS_TOKEN_COOKIE = "access_token"
REFRESH_TOKEN_COOKIE = "refresh_token"


# ── Helpers ───────────────────────────────────────────────────────

def _cookie_kwargs(max_age: int) -> dict:
    """Common kwargs for auth cookies."""
    return {
        "httponly": True,           # JS can't read it — XSS safe
        "samesite": "lax",          # CSRF safe for same-site navigations
        "secure": settings.COOKIE_SECURE,  # HTTPS only in production
        "path": "/",                # Available on every route
        "max_age": max_age,
    }


def set_access_token_cookie(response: Response, token: str) -> None:
    """Set the access_token httpOnly cookie."""
    max_age = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=token,
        **_cookie_kwargs(max_age),
    )


def set_refresh_token_cookie(response: Response, token: str) -> None:
    """Set the refresh_token httpOnly cookie."""
    max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE,
        value=token,
        **_cookie_kwargs(max_age),
    )


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """Set both auth cookies on a response."""
    set_access_token_cookie(response, access_token)
    set_refresh_token_cookie(response, refresh_token)


def clear_auth_cookies(response: Response) -> None:
    """Clear both auth cookies (used on logout)."""
    response.delete_cookie(
        key=ACCESS_TOKEN_COOKIE,
        path="/",
    )
    response.delete_cookie(
        key=REFRESH_TOKEN_COOKIE,
        path="/",
    )
