"""Find the open backlog items that carry one ID."""

from __future__ import annotations

from tadu.item_id import item_id
from tadu.matching_items import matching_items


def items_with_id(lines: list[str], fenced: list[bool], uid: str) -> list[int]:
    """Indices of top-level open items outside fences whose ID field is `uid`."""
    return [
        index for index in matching_items(lines, fenced, "") if item_id(lines, fenced, index) == uid
    ]
