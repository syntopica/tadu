"""Print the git history of one card's item."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.item_history import item_history

if TYPE_CHECKING:
    from tadu.card import Card


def print_item_history(card: Card) -> int:
    """Print the commits that touched the item; exit 1 when git has no answer."""
    item = card.item
    history = item_history(card.root, item.path, item.line, item.end_line)
    if history is None:
        print(f"tadu show: no git history for {item.path}", file=sys.stderr)
        return 1
    print(history, end="")
    return 0
