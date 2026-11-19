"""The path of a request as the board names it, wherever it is served."""

from __future__ import annotations


def board_path(path: str, base: str) -> str | None:
    """The request path without the public URL's path, or None when it is that path alone.

    A board in a subfolder (`base`, such as `/tadu`) gets its requests from a proxy that
    either keeps the subfolder (`/tadu/api/cards`) or takes it away (`/api/cards`); both
    come out as `/api/cards`. The subfolder alone, without its slash, is None: the page's
    relative links need the slash, so the caller redirects. The query string stays.
    """
    if not base:
        return path
    route, mark, query = path.partition("?")
    if route == base:
        return None
    if route.startswith(f"{base}/"):
        return route.removeprefix(base) + mark + query
    return path
