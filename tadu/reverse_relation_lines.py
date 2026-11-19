"""The relations that point at a card, as `tadu show` prints them."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.format_card_line import format_card_line
from tadu.reverse_relation_index import reverse_relation_index
from tadu.short_keys import short_keys

if TYPE_CHECKING:
    from tadu.card import Card


def reverse_relation_lines(card: Card, cards: tuple[Card, ...]) -> tuple[str, ...]:
    """`<reverse name>: <card line>` for every loaded card whose relations name this card."""
    shown = short_keys(tuple(other.item.key for other in cards))
    pointing = reverse_relation_index(cards).get(card.item.key, [])
    return tuple(
        f"{name}: {format_card_line(other, shown[other.item.key])}" for name, other in pointing
    )
