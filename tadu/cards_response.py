"""The card data response."""

from __future__ import annotations

import json
import sys
from http import HTTPStatus
from typing import TYPE_CHECKING

from tadu.board_payload import board_payload
from tadu.json_error import json_error
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    from collections.abc import Callable
    from datetime import date

    from tadu.board_state import BoardState
    from tadu.local_config import LocalConfig
    from tadu.payload_view import PayloadView
    from tadu.workspace import Workspace


def cards_response(
    state: BoardState,
    today: date,
    narrow: Callable[[Workspace, LocalConfig], PayloadView] | None = None,
) -> tuple[int, bytes, str]:
    """The payload as JSON; 500 when the workspace no longer loads.

    The error names what is wrong, which can be a repository the person may not know of,
    so on a board that signs in with GitHub (`narrow` given) it goes to the operator on
    standard error and the page gets a message that names nothing.

    SignedOutError from `narrow` escapes.
    """
    try:
        payload = board_payload(state, today, narrow)
    except WorkspaceError as error:
        if narrow is None:
            return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, str(error))
        sys.stderr.write(f"tadu board: {error}\n")
        message = "the workspace does not load; the board's operator can see why"
        return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, message)
    body = json.dumps(payload, ensure_ascii=False).encode()
    return HTTPStatus.OK, body, "application/json; charset=utf-8"
