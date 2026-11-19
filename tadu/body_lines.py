"""The lines of an item that are neither its title nor its fields."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.fenced_lines import fenced_lines
from tadu.field_values import field_values
from tadu.title_end import title_end

if TYPE_CHECKING:
    from tadu.backlog_item import BacklogItem


def body_lines(item: BacklogItem) -> list[str]:
    """The non-blank lines after the title paragraph that are not field lines, as written."""
    lines = item.text.split("\n")
    fenced = fenced_lines(lines)
    fields = {index for index, _, _ in field_values(lines, fenced, 0, len(lines))}
    start = title_end(lines, fenced, 0)
    return [
        line
        for index, line in enumerate(lines[start:], start)
        if line.strip() and index not in fields
    ]
