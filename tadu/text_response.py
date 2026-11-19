"""A plain-text response for a person, not for the page's scripts."""

from __future__ import annotations


def text_response(status: int, message: str) -> tuple[int, bytes, str]:
    """Status, the message and a line pointing back to the board."""
    body = f"{message}\n\nOpen the board's address again to sign in.\n".encode()
    return status, body, "text/plain; charset=utf-8"
