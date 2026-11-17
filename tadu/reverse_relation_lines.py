"""The relations that point at a card, which its own file does not store."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.format_card_line import format_card_line
from tadu.reverse_relation_names import REVERSE_RELATION_NAMES
from tadu.short_keys import short_keys

if TYPE_CHECKING:
    from tadu.card import Card


def reverse_relation_lines(card: Card, cards: tuple[Card, ...]) -> tuple[str, ...]:
    """`<reverse name>: <card line>` for every loaded card whose relations name this card."""
    key = card.item.key
    shown = short_keys(tuple(other.item.key for other in cards))
    lines = [
        f"{REVERSE_RELATION_NAMES[kind]}: {format_card_line(other, shown[other.item.key])}"
        for other in cards
        for kind, target in other.item.extras.relations
        if target == key
    ]
    return tuple(lines)
