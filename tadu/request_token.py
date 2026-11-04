"""The board token a request presents."""

from __future__ import annotations

from urllib.parse import parse_qs


def request_token(path: str, header: str | None) -> str | None:
    """The `token` query parameter, else the X-Tadu-Token header value, else None."""
    query = parse_qs(path.partition("?")[2]).get("token")
    return query[0] if query else header
