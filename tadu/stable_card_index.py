"""Cards by their `ID:`, preferring an open card when an ID repeats."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.open_states import OPEN_STATES

if TYPE_CHECKING:
    from tadu.card import Card


def stable_card_index(cards: tuple[Card, ...]) -> dict[str, Card]:
    """The first open card for each ID, else the first closed one; derived keys are left out."""
    index: dict[str, Card] = {}
    for card in cards:
        if not card.item.stable:
            continue
        known = index.get(card.item.key)
        if known is None or (
            known.item.state not in OPEN_STATES and card.item.state in OPEN_STATES
        ):
            index[card.item.key] = card
    return index
