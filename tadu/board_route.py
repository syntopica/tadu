"""Answer an authorized GET of the board by its path."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from tadu.board_asset import board_asset
from tadu.board_asset_name import board_asset_name
from tadu.board_cards import board_cards
from tadu.board_data_path import BOARD_DATA_PATH
from tadu.json_error import json_error

if TYPE_CHECKING:
    from datetime import date

    from tadu.board_state import BoardState


def board_route(target: str, state: BoardState, today: date) -> tuple[int, bytes, str]:
    """Status, body and content type for a request target: a path and its query string.

    The cards answer from the workspace; any other path is a page asset or 404.
    """
    path, _, query = target.partition("?")
    if path == BOARD_DATA_PATH:
        return board_cards(state, query, today)
    asset = board_asset(board_asset_name(path))
    if asset is None:
        return json_error(HTTPStatus.NOT_FOUND, "not found")
    return HTTPStatus.OK, *asset
