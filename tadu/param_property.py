"""One property of a tool's input schema."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.param_help import param_help

if TYPE_CHECKING:
    from tadu.param import Param

TYPES = {
    "count": "integer",
    "flag": "boolean",
    "switch": "boolean",
    "list": "array",
    "words": "array",
}


def param_property(param: Param) -> dict[str, object]:
    """A JSON Schema property: a string (a day as YYYY-MM-DD), a count, a boolean or strings.

    A choice is an enum, and a day's description says its form.
    """
    kind = TYPES.get(param.kind, "string")
    help_text = param_help(param)
    description = f"YYYY-MM-DD; {help_text}" if param.kind == "day" else help_text
    schema: dict[str, object] = {"type": kind, "description": description}
    if kind == "array":
        schema["items"] = {"type": "string"}
    if kind == "integer":
        schema["minimum"] = 0
    if param.kind == "choice":
        schema["enum"] = list(param.choices)
    return schema
