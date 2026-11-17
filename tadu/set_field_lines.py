"""An open item with one field set: replaced in place, or added as its last paragraph."""

from __future__ import annotations

from tadu.fenced_lines import fenced_lines
from tadu.field_values import field_values
from tadu.item_span_end import item_span_end


def set_field_lines(lines: list[str], first: int, name: str, value: str) -> list[str]:
    """The lines with `  name: value` on the item at `first`.

    shortcut: a repeated field is left alone beyond its first line, `tadu doctor` reports it.
    """
    end = item_span_end(lines, first)
    changed = [*lines]
    for index, found, _ in field_values(lines, fenced_lines(lines), first, end):
        if found == name:
            # keys: index is a line number, unique within the list.
            changed[index] = f"  {name}: {value.strip()}"
            return changed
    changed[end:end] = ["", f"  {name}: {value.strip()}"]
    return changed
