"""Where an ID paragraph goes inside an item."""

from __future__ import annotations

from tadu.item_fenced_lines import item_fenced_lines
from tadu.item_span_end import item_span_end


def id_insert_index(lines: list[str], fenced: list[bool], first: int) -> int:
    """Index just after the item's first paragraph, before any blank line or fence."""
    end = item_span_end(lines, first)
    inside = item_fenced_lines(lines, fenced, first, end)
    index = first + 1
    while index < end and lines[index].strip() and not inside[index]:
        index += 1
    return index
