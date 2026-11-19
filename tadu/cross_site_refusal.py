"""Refuse a request for the board's data or session that another page made."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

from tadu.board_data_path import BOARD_CHECK_PATH, BOARD_DATA_PATH
from tadu.board_operation_path import BOARD_OPERATION_PATH
from tadu.json_error import json_error
from tadu.sign_in_settings import SIGN_OUT_PATH

if TYPE_CHECKING:
    from email.message import Message

GUARDED_PATHS = frozenset({BOARD_DATA_PATH, BOARD_CHECK_PATH, SIGN_OUT_PATH})


def cross_site_refusal(
    hosts: frozenset[str], path: str | None, headers: Message
) -> tuple[int, bytes, str] | None:
    """403 when a browser says another page asked for the cards, the check, a sign-out or a call.

    SameSite=Lax keeps the session cookie off requests from other sites, but not from
    other origins of the same site: a page on a sibling subdomain could load the cards
    (which counts as use, and asks GitHub), report activity, sign someone out or run a call as them. So the
    board's own page must be the one asking: `Sec-Fetch-Site`, which browsers send and
    pages cannot forge, must be `same-origin`, and an `Origin` (sent with every POST)
    must be the board's. A client that sends neither, such as curl, needs the cookie.
    """
    route = "" if path is None else path.partition("?")[0]
    if route not in GUARDED_PATHS and not route.startswith(BOARD_OPERATION_PATH):
        return None
    site, origin = headers.get("Sec-Fetch-Site"), headers.get("Origin")
    foreign_origin = origin is not None and urlsplit(origin).netloc not in hosts
    if (site is not None and site != "same-origin") or foreign_origin:
        status = HTTPStatus.FORBIDDEN
        return json_error(status, "refused: the request did not come from the board's page")
    return None
