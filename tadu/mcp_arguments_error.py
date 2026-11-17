"""Check a tool call's arguments against the tool's input schema."""

from __future__ import annotations

from tadu.mcp_value_error import mcp_value_error


def mcp_arguments_error(schema: dict[str, object], arguments: object) -> str | None:
    """Why the arguments do not fit the schema, or None."""
    if not isinstance(arguments, dict):
        return "arguments must be an object"
    properties: dict[str, dict[str, object]] = schema["properties"]  # type: ignore[assignment]
    required: list[str] = schema["required"]  # type: ignore[assignment]
    unknown = sorted(set(arguments) - set(properties))
    missing = [name for name in required if name not in arguments]
    if unknown or missing:
        return (
            f"unknown arguments: {', '.join(unknown)}"
            if unknown
            else (f"missing arguments: {', '.join(missing)}")
        )
    problems = (mcp_value_error(name, properties[name], value) for name, value in arguments.items())
    return next((problem for problem in problems if problem is not None), None)
