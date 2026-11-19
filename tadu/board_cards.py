"""The board's card data."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING
from urllib.parse import parse_qs

from tadu.board_payload import board_payload
from tadu.json_error import json_error
from tadu.json_response import json_response
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    from datetime import date

    from tadu.board_state import BoardState

LONGEST = 36500


def board_cards(state: BoardState, query: str, today: date) -> tuple[int, bytes, str]:
    """Status, body and content type of the card data, `?done_days=N` back (default: --done-days).

    400 for a window that is not a whole number of days from 0 to 36500; 500 when the
    workspace does not load.
    """
    asked = parse_qs(query).get("done_days", [str(state.done_days)])[0]
    if not (asked.isascii() and asked.isdecimal()) or int(asked) > LONGEST:
        return json_error(HTTPStatus.BAD_REQUEST, f"done_days must be 0 to {LONGEST}")
    try:
        payload = board_payload(state, int(asked), today)
    except WorkspaceError as error:
        return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, str(error))
    return json_response(HTTPStatus.OK, payload)
