"""Answer an authorized board request by its path."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from tadu.board_asset import board_asset
from tadu.board_asset_name import board_asset_name
from tadu.board_data_path import BOARD_CHECK_PATH, BOARD_DATA_PATH
from tadu.cards_response import cards_response
from tadu.json_error import json_error

if TYPE_CHECKING:
    from datetime import date

    from tadu.board_state import BoardState


def board_route(path: str, state: BoardState, today: date) -> tuple[int, bytes, str]:
    """Status, body and content type for a path without its query string."""
    if path == BOARD_DATA_PATH:
        return cards_response(state, today)
    if path == BOARD_CHECK_PATH:
        return HTTPStatus.OK, b'{"ok": true}', "application/json; charset=utf-8"
    asset = board_asset(board_asset_name(path))
    if asset is None:
        return json_error(HTTPStatus.NOT_FOUND, "not found")
    return HTTPStatus.OK, *asset
