"""The board token a request presents."""

from __future__ import annotations

from urllib.parse import parse_qs


def request_token(path: str, cookie: str | None) -> str | None:
    """The `token` query parameter, else the first `tadu_board` cookie value, else None.

    The Cookie header is split by hand: SimpleCookie drops every cookie in the
    header when any one of them is malformed, so a stray cookie from another
    local site would lock the board out.
    """
    query = parse_qs(path.partition("?")[2]).get("token")
    if query:
        return query[0]
    for pair in (cookie or "").split(";"):
        name, separator, value = pair.strip().partition("=")
        if separator and name == "tadu_board":
            return value
    return None
