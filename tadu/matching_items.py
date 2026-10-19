"""Find the open backlog items whose first line contains a text."""

from __future__ import annotations

from tadu.open_item_pattern import OPEN_ITEM_PATTERN


def matching_items(lines: list[str], fenced: list[bool], text: str) -> list[int]:
    """Indices of top-level open items outside fences whose first line contains `text`."""
    return [
        index
        for index, line in enumerate(lines)
        if not fenced[index] and OPEN_ITEM_PATTERN.match(line) and text in line
    ]
