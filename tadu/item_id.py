"""Read the ID an item carries."""

from __future__ import annotations

from tadu.field_values import field_values
from tadu.item_fenced_lines import item_fenced_lines
from tadu.item_span_end import item_span_end


def item_id(lines: list[str], fenced: list[bool], first: int) -> str | None:
    """The value of the item's first ID field outside its fences, or None when it has none."""
    end = item_span_end(lines, first)
    values = field_values(lines, item_fenced_lines(lines, fenced, first, end), first, end)
    return next((value for _, name, value in values if name == "ID"), None)
