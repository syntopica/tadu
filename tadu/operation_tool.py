"""One operation as a tool, as MCP's `tools/list` gives it."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.param_property import param_property
from tadu.tool_params import tool_params

if TYPE_CHECKING:
    from tadu.operation import Operation


def operation_tool(operation: Operation) -> dict[str, object]:
    """Name, description, input schema and hints: only admin operations are destructive.

    An argument is required when it is required on its own, not as one of a group.
    """
    params = tool_params(operation)
    return {
        "name": operation.name,
        "description": operation.describe or operation.help,
        "inputSchema": {
            "type": "object",
            # keys: argument names are unique within an operation; test_operations checks it.
            "properties": {param.name: param_property(param) for param in params},
            "required": [p.name for p in params if p.required and not p.exclusive],
            "additionalProperties": False,
        },
        "annotations": {
            "readOnlyHint": operation.access == "read",
            "destructiveHint": operation.access == "admin",
            "idempotentHint": operation.access == "read",
            "openWorldHint": False,
        },
    }
