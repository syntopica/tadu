"""The name a session is stored under."""

from __future__ import annotations

from tadu.session_secret import session_secret


def session_id(cookie: str) -> str:
    """Derived from the cookie: it finds the session without revealing the cookie."""
    return session_secret(cookie, "id").hex()
