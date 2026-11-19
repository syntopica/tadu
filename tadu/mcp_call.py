"""Run one MCP tool call."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.operations import OPERATIONS
from tadu.run_operation import run_operation

if TYPE_CHECKING:
    from tadu.operation_host import OperationHost


def mcp_call(name: str, arguments: object, host: OperationHost) -> dict[str, object]:
    """The `tools/call` result: the command's output then its errors as text.

    It is an error when the command refused (exit 2), or when a reading command other than
    doctor exits 1 (`show` found no item). A change that exits 1 was written and then had
    `tadu doctor` find errors in the backlog, and doctor's 1 is its report: calling again
    would repeat a change already made, so neither is an error. The command reads no config
    file (see operation_argv): a tool does what its schema says, whatever defaults a person
    set for their own use.
    """
    code, out, err = run_operation(name, arguments, host)
    operation = OPERATIONS.get(name)
    reported = code == 1 and operation is not None and (operation.writes or name == "doctor")
    return {
        "content": [{"type": "text", "text": (out + err).strip() or "Nothing found."}],
        "isError": code != 0 and not reported,
    }
