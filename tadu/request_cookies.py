"""The cookies a request carries."""

from __future__ import annotations

from werkzeug.http import parse_cookie


def request_cookies(header: str | None) -> dict[str, str]:
    """Cookie values by name from a Cookie header, parsed by Werkzeug.

    Not http.cookies.SimpleCookie: it drops every cookie after one it cannot parse,
    and other sites' cookies on the same host (a JSON value, a space, an accent) would
    hide the session. When a name repeats, the first value wins, as browsers send the
    most specific first. The header is as http.server gives it, bytes read as latin-1.
    """
    parsed = parse_cookie(header or "")
    # keys: a MultiDict's keys, each once; [] gives a repeated name's first value.
    return {name: parsed[name] for name in parsed}
