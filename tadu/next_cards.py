"""What an agent can do next without a person."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.card_section import card_section
from tadu.held_by import held_by
from tadu.is_deferred import is_deferred
from tadu.open_cards import open_cards

if TYPE_CHECKING:
    from datetime import date

    from tadu.card import Card


def next_cards(cards: tuple[Card, ...], person: str | None, today: date) -> list[Card]:
    """Open tasks and unclassified items that can go on now, most pressing first.

    Left out: other kinds, blocked items, items whose `Not before:` is ahead and
    items assigned only to others. An unclassified item counts as work, as every
    item did before kinds existed; `Kind:` is what takes it out.
    """
    return [
        card
        for card in open_cards(cards)
        if card_section(card) == "do" and held_by(card, person) and not is_deferred(card, today)
    ]
