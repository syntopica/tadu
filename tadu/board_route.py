"""Answer an authorized board request by its path."""

from __future__ import annotations

import json
from http import HTTPStatus
from typing import TYPE_CHECKING

from tadu.board_asset import board_asset
from tadu.board_asset_paths import BOARD_ASSET_PATHS
from tadu.board_data_path import BOARD_DATA_PATH
from tadu.board_payload import board_payload
from tadu.json_error import json_error
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    from datetime import date

    from tadu.board_state import BoardState


def board_route(path: str, state: BoardState, today: date) -> tuple[int, bytes, str]:
    """Status, body and content type for a path without its query string."""
    if path == BOARD_DATA_PATH:
        try:
            payload = board_payload(state, today)
        except WorkspaceError as error:
            return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, str(error))
        body = json.dumps(payload, ensure_ascii=False).encode()
        return HTTPStatus.OK, body, "application/json; charset=utf-8"
    asset = board_asset(BOARD_ASSET_PATHS.get(path, ""))
    if asset is None:
        return json_error(HTTPStatus.NOT_FOUND, "not found")
    return HTTPStatus.OK, *asset
