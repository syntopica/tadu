"""The closed cards of a scope, newest first."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.card import Card


def recently_done(cards: tuple[Card, ...]) -> tuple[Card, ...]:
    """Done and cancelled cards by closing day, newest first; ties keep their read order."""
    closed = (card for card in cards if card.item.state in "x-")
    return tuple(sorted(closed, key=lambda card: card.item.day or date.min, reverse=True))
