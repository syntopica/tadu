"""The Set-Cookie value that lets the page fetch without the token in its URL."""

from __future__ import annotations


def board_cookie(token: str) -> str:
    """An HttpOnly, SameSite=Strict cookie carrying the token for the whole site."""
    return f"tadu_board={token}; HttpOnly; SameSite=Strict; Path=/"
