"""Build the item selector a close request asks for."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.select_item import select_item
from tadu.select_item_by_id import select_item_by_id

if TYPE_CHECKING:
    from tadu.item_selector import ItemSelector


def close_selector(text: str, *, by_id: bool) -> ItemSelector:
    """Select by the item's ID field when by_id, otherwise by text in its first line."""
    if by_id:
        return lambda lines, name: select_item_by_id(lines, text, name)
    return lambda lines, name: select_item(lines, text, name)
