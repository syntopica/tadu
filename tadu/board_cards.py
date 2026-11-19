"""The board's card data."""

from __future__ import annotations

import sys
from http import HTTPStatus
from typing import TYPE_CHECKING
from urllib.parse import parse_qs

from tadu.board_payload import board_payload
from tadu.json_error import json_error
from tadu.json_response import json_response
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    from collections.abc import Callable
    from datetime import date

    from tadu.board_state import BoardState
    from tadu.local_config import LocalConfig
    from tadu.payload_view import PayloadView
    from tadu.workspace import Workspace

LONGEST = 36500


def board_cards(
    state: BoardState,
    query: str,
    today: date,
    narrow: Callable[[Workspace, LocalConfig], PayloadView] | None = None,
) -> tuple[int, bytes, str]:
    """Status, body and content type of the card data, `?done_days=N` back (default: --done-days).

    400 for a window that is not a whole number of days from 0 to 36500; 500 when the
    workspace does not load. The error names what is wrong, which can be a repository the
    person may not know of, so on a board that signs in with GitHub (`narrow` given) it goes
    to the operator on standard error and the page gets a message that names nothing.

    SignedOutError from `narrow` escapes.
    """
    asked = parse_qs(query).get("done_days", [str(state.done_days)])[0]
    if not (asked.isascii() and asked.isdecimal()) or int(asked) > LONGEST:
        return json_error(HTTPStatus.BAD_REQUEST, f"done_days must be 0 to {LONGEST}")
    try:
        payload = board_payload(state, int(asked), today, narrow)
    except WorkspaceError as error:
        if narrow is None:
            return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, str(error))
        (sys.__stderr__ or sys.stderr).write(f"tadu board: {error}\n")
        message = "the workspace does not load; the board's operator can see why"
        return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, message)
    return json_response(HTTPStatus.OK, payload)
