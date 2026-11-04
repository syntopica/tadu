"""Parse the field lines of one item."""

from __future__ import annotations

from datetime import date

from tadu.field_checks import FIELD_CHECKS
from tadu.field_problem import FieldProblem
from tadu.item_fields import ItemFields
from tadu.split_list_value import split_list_value


def parse_item_fields(
    values: list[tuple[int, str, str]],
) -> tuple[ItemFields, tuple[FieldProblem, ...]]:
    """Fields of an item; invalid or repeated values become problems."""
    parsed: dict[str, object] = {}
    problems: list[FieldProblem] = []
    seen: set[str] = set()
    for line, name, value in values:
        if name in seen:
            problems.append(FieldProblem(line, f"{name} appears more than once"))
            continue
        seen.add(name)
        message = FIELD_CHECKS[name](value)
        if message is not None:
            problems.append(FieldProblem(line, message))
        elif name in ("Assignees", "Labels"):
            parsed[name.lower()] = split_list_value(value)
        elif name == "Due":
            parsed["due"] = date.fromisoformat(value)
        elif name == "Estimate":
            parsed["estimate"] = int(value)
        else:
            parsed["id" if name == "ID" else name.lower()] = value
    return ItemFields(**parsed), tuple(problems)  # type: ignore[arg-type]
