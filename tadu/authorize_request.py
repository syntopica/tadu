"""Decide whether a board request may be answered."""

from __future__ import annotations

import hmac
from http import HTTPStatus
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.board_state import BoardState


def authorize_request(host_header: str | None, token: str | None, state: BoardState) -> int | None:
    """421 for a Host other than the bound address, 403 for a wrong token, else None."""
    if host_header not in state.allowed_hosts:
        return HTTPStatus.MISDIRECTED_REQUEST
    if token is None or not hmac.compare_digest(token.encode(), state.token.encode()):
        return HTTPStatus.FORBIDDEN
    return None
