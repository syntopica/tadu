"""Answer one tool call the board page posts."""

from __future__ import annotations

import json
from http import HTTPStatus
from typing import TYPE_CHECKING

from tadu.board_operation_path import BOARD_OPERATION_PATH
from tadu.captured_run import INTERNAL_ERROR
from tadu.json_error import json_error
from tadu.json_response import json_response
from tadu.operation_host import OperationHost
from tadu.operation_tools import operation_tools
from tadu.run_operation import run_operation
from tadu.scope import Scope

if TYPE_CHECKING:
    from tadu.board_state import BoardState


def board_call(
    path: str, body: bytes, state: BoardState, *, trace: bool = True
) -> tuple[int, bytes, str]:
    """Status, body and content type for a call to `/api/op/<name>` with JSON arguments.

    The call runs as `tadu mcp` runs it, over the board's workspace: 404 for no such tool,
    403 for one the board's --allow does not permit, 400 for a body that is not a JSON
    object. Otherwise 200 with the command's exit `code`, `output` and `errors`: arguments
    that do not fit, and refusals such as a repository whose access is read, are exit 2.
    A command that fails unexpectedly says so with its traceback, unless `trace` is False
    (a board for strangers, which must not show the machine's paths).
    """
    name = path.partition("?")[0].removeprefix(BOARD_OPERATION_PATH)
    if not path.startswith(BOARD_OPERATION_PATH) or name not in operation_tools("admin"):
        return json_error(HTTPStatus.NOT_FOUND, "not found")
    if name not in operation_tools(state.allow):
        message = f"this board allows {state.allow} only; start it with a higher --allow"
        return json_error(HTTPStatus.FORBIDDEN, message)
    try:
        arguments = json.loads(body.decode())
    except (UnicodeDecodeError, ValueError, RecursionError):
        arguments = None
    if not isinstance(arguments, dict):
        return json_error(HTTPStatus.BAD_REQUEST, "the body must be a JSON object of arguments")
    host = OperationHost(Scope(workspace=str(state.workspace)), state.allow, state.main)
    code, output, errors = run_operation(name, arguments, host)
    if code == INTERNAL_ERROR and not trace:
        errors = f"tadu {name}: internal error\n"
    return json_response(HTTPStatus.OK, {"code": code, "output": output, "errors": errors})
