"""One MCP tool definition."""

from __future__ import annotations


def mcp_tool(  # noqa: PLR0913 - the four parts of a tool and its one hint
    name: str,
    description: str,
    properties: dict[str, dict[str, object]],
    required: tuple[str, ...] = (),
    *,
    read_only: bool = True,
) -> dict[str, object]:
    """The tool as `tools/list` returns it; a writing tool is additive, never destructive."""
    return {
        "name": name,
        "description": description,
        "inputSchema": {
            "type": "object",
            "properties": properties,
            "required": list(required),
            "additionalProperties": False,
        },
        "annotations": {
            "readOnlyHint": read_only,
            "destructiveHint": False,
            "idempotentHint": read_only,
            "openWorldHint": False,
        },
    }
