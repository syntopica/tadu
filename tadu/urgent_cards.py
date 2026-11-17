"""What needs attention now, whoever acts on it."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from tadu.card_section import card_section
from tadu.is_deferred import is_deferred
from tadu.open_cards import open_cards

if TYPE_CHECKING:
    from datetime import date

    from tadu.card import Card


def urgent_cards(cards: tuple[Card, ...], today: date, days: int) -> list[tuple[str, Card]]:
    """(section, card) for open items of urgent or high priority, or dated within `days`.

    The dates are the `Due:` deadline and the `Check on:` day; an overdue one always
    counts. An item whose `Not before:` is still ahead is not urgent yet.
    """
    horizon = today + timedelta(days=days)
    return [
        (card_section(card), card)
        for card in open_cards(cards)
        if not is_deferred(card, today)
        and (
            card.item.fields.priority in ("urgent", "high")
            or any(
                day is not None and day <= horizon
                for day in (card.item.fields.due, card.item.fields.check_on)
            )
        )
    ]
