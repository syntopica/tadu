"""Decide whether a board request may be answered."""

from __future__ import annotations

import hmac
from http import HTTPStatus
from typing import TYPE_CHECKING

from tadu.board_data_path import BOARD_DATA_PATH

if TYPE_CHECKING:
    from tadu.board_state import BoardState


def authorize_request(
    host_header: str | None, token: str | None, route: str, state: BoardState
) -> int | None:
    """421 for a Host other than the bound address; 403 for a wrong token on the data path."""
    if host_header not in state.allowed_hosts:
        return HTTPStatus.MISDIRECTED_REQUEST
    if route != BOARD_DATA_PATH:
        return None
    if token is None or not hmac.compare_digest(token.encode(), state.token.encode()):
        return HTTPStatus.FORBIDDEN
    return None
