"""Pick the card `tadu show` prints."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.cards_by_key import cards_by_key

if TYPE_CHECKING:
    from tadu.card import Card


def shown_card(cards: tuple[Card, ...], key: str) -> Card | None:
    """The card a key or unique task-id prefix names; None after explaining on stderr why not."""
    found = cards_by_key(cards, key)
    keys = sorted({card.item.key for card in found})
    if not found:
        print(f"tadu show: no item {key}", file=sys.stderr)
        return None
    if len(keys) > 1:
        print(f"tadu show: {key} is ambiguous: {', '.join(keys)}", file=sys.stderr)
        return None
    if len(found) > 1:
        print(f"tadu show: {key} matches {len(found)} items; showing the first", file=sys.stderr)
    return found[0]
