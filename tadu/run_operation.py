"""Run one tool call, for MCP or the board."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.arguments_error import arguments_error
from tadu.canonical_arguments import canonical_arguments
from tadu.captured_run import captured_run
from tadu.operation_argv import operation_argv
from tadu.operation_lock import OPERATION_LOCK
from tadu.operation_tools import operation_tools
from tadu.operations import OPERATIONS
from tadu.tool_params import tool_params

if TYPE_CHECKING:
    from tadu.operation_host import OperationHost


def run_operation(name: str, arguments: object, host: OperationHost) -> tuple[int, str, str]:
    """(exit status, output, errors) of the operation run as the command line would run it.

    Arguments may use an argument's other names (see canonical_arguments). A tool the host's
    access level does not offer, or arguments that do not fit its schema, exit 2 without
    running anything. Calls take turns (see OPERATION_LOCK).
    """
    tool = operation_tools(host.allow).get(name)
    if tool is None:
        return 2, "", f"no tool {name} at access level {host.allow}"
    operation = OPERATIONS[name]
    given = canonical_arguments(tool_params(operation), arguments)
    problem = arguments_error(tool["inputSchema"], given)  # type: ignore[arg-type]
    if problem is not None:
        return 2, "", problem
    argv = operation_argv(operation, given, host.scope)  # type: ignore[arg-type]
    with OPERATION_LOCK:
        return captured_run(host.main, argv)
