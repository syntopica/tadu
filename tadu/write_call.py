"""Tell a call that changes files from every other."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from tadu.board_operation_path import BOARD_OPERATION_PATH
from tadu.canonical_arguments import canonical_arguments
from tadu.operation_tools import operation_tools
from tadu.operations import OPERATIONS
from tadu.tool_params import tool_params

if TYPE_CHECKING:
    from tadu.board_state import BoardState


def write_call(path: str, body: bytes, state: BoardState) -> tuple[str, dict[str, object]] | None:
    """The operation and its arguments (under their own names) when the call would write.

    None for a call that reads, for a preview, which writes nothing, and for one the board
    refuses (board_call says why): none of them is a change to propose.
    """
    name = path.partition("?")[0].removeprefix(BOARD_OPERATION_PATH)
    if not path.startswith(BOARD_OPERATION_PATH) or name not in operation_tools(state.allow):
        return None
    operation = OPERATIONS[name]
    try:
        given = canonical_arguments(tool_params(operation), json.loads(body.decode()))
    except (UnicodeDecodeError, ValueError, RecursionError):
        return None
    if not operation.writes or not isinstance(given, dict) or given.get("preview") is True:
        return None
    return name, given
