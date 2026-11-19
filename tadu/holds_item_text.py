"""Tell whether a backlog text holds an item exactly."""

from __future__ import annotations

from tadu.item_ends_at import item_ends_at


def holds_item_text(text: str, item: str) -> bool:
    """True when `item` (an item's lines joined with line feeds) is a whole item of `text`.

    A cheap test that spares parsing a file version in which the item did not change.
    """
    start = text.find(item)
    while start != -1:
        if (start == 0 or text[start - 1] == "\n") and item_ends_at(text, start + len(item)):
            return True
        start = text.find(item, start + 1)
    return False
