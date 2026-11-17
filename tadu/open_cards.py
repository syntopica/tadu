"""The open cards of a scope, most pressing first."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.attention_order import attention_order

if TYPE_CHECKING:
    from tadu.card import Card


def open_cards(cards: tuple[Card, ...]) -> list[Card]:
    """Cards still in a backlog (not done or cancelled), by attention order; ties keep read order."""
    return sorted((card for card in cards if card.item.state not in "x-"), key=attention_order)
