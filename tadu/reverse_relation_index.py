"""The relations that point at each card, which the card's own file does not store."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.reverse_relation_names import REVERSE_RELATION_NAMES

if TYPE_CHECKING:
    from tadu.card import Card


def reverse_relation_index(cards: tuple[Card, ...]) -> dict[str, list[tuple[str, Card]]]:
    """Item key to (reverse name, card) of each loaded card whose relations name it, in order."""
    index: dict[str, list[tuple[str, Card]]] = {}
    for other in cards:
        for kind, target in other.item.extras.relations:
            # keys: one list per target key, grown as each relation naming it is met.
            index.setdefault(target, []).append((REVERSE_RELATION_NAMES[kind], other))
    return index
