"""One property of an MCP tool's input schema."""

from __future__ import annotations


def mcp_property(
    kind: str, description: str, values: tuple[str, ...] | None = None
) -> dict[str, object]:
    """A JSON Schema property: string, integer, boolean, or array of strings; `values` is an enum."""
    schema: dict[str, object] = {"type": kind, "description": description}
    if kind == "array":
        schema["items"] = {"type": "string"}
    if kind == "integer":
        schema["minimum"] = 0
    if values is not None:
        schema["enum"] = list(values)
    return schema
