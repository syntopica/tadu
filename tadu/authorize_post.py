"""Decide whether a tool call posted to the board may be read."""

from __future__ import annotations

import hmac
from http import HTTPStatus
from typing import TYPE_CHECKING

from tadu.board_body_limit import BOARD_BODY_LIMIT

if TYPE_CHECKING:
    from email.message import Message

    from tadu.board_state import BoardState


def authorize_post(headers: Message, state: BoardState) -> tuple[int, str] | None:
    """The refusal (status and why), or None when the call comes from the board's own page.

    The Host must be the bound address (421); the token must come as the X-Tadu-Token header,
    never in the address (403), unless the board signs in with GitHub, where the caller checks
    the session cookie instead (and Origin names the public URL's scheme); Origin and Sec-Fetch-Site, when the browser sends them (Chrome
    sends no Origin on a call to the page's own server), must name the board's own origin
    (403); the body must be JSON (415) of a stated length (411) no larger than
    BOARD_BODY_LIMIT (413). Another site's page cannot meet these: it has no token, and a
    custom header or a JSON body makes its browser ask first, which the board refuses; nor can
    it read any answer, since no response carries a CORS header.
    """
    host, token = headers.get("Host"), headers.get("X-Tadu-Token")
    github = state.github
    origin = f"{'https' if github is not None and github.secure else 'http'}://{host}"
    length = headers.get("Content-Length", "")
    stated = length.isascii() and length.isdecimal()
    kind = headers.get("Content-Type", "").partition(";")[0].strip().lower()
    checks = (
        (host not in state.allowed_hosts, HTTPStatus.MISDIRECTED_REQUEST, "misdirected request"),
        (
            github is None
            and (token is None or not hmac.compare_digest(token.encode(), state.token.encode())),
            HTTPStatus.FORBIDDEN,
            "forbidden",
        ),
        (
            headers.get("Origin", origin) != origin,
            HTTPStatus.FORBIDDEN,
            "cross-origin call",
        ),
        (
            headers.get("Sec-Fetch-Site", "same-origin") != "same-origin",
            HTTPStatus.FORBIDDEN,
            "cross-site call",
        ),
        (kind != "application/json", HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "send JSON"),
        (not stated, HTTPStatus.LENGTH_REQUIRED, "length required"),
        (
            stated and int(length) > BOARD_BODY_LIMIT,
            HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
            "call too large",
        ),
    )
    return next(((status, why) for refused, status, why in checks if refused), None)
