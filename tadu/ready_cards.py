"""The open cards nothing blocks or defers."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from tadu.deferred_family import deferred_family
from tadu.priority_rank import priority_rank

if TYPE_CHECKING:
    from tadu.card import Card


def ready_cards(
    cards: tuple[Card, ...], today: date, *, with_deferred_children: bool = False
) -> tuple[Card, ...]:
    """Pending and in-progress cards with no open blocked_by task and no future defer_until.

    Most urgent first, then nearest due date, then title. A blocked_by target that is not among
    the cards (closed long ago, or missing) does not block. The children of a deferred parent are
    left out unless `with_deferred_children`.
    """
    held_back = frozenset() if with_deferred_children else deferred_family(cards, today)
    open_keys = {card.item.key for card in cards if card.item.state in " ~!"}
    kept = [
        card
        for card in cards
        if card.item.state in " ~"
        and card.item.key not in held_back
        and not any(
            kind == "blocked_by" and key in open_keys for kind, key in card.item.extras.relations
        )
        and (card.item.extras.defer_until is None or card.item.extras.defer_until <= today)
    ]
    return tuple(
        sorted(
            kept,
            key=lambda card: (
                priority_rank(card.item.fields.priority),
                card.item.fields.due or date.max,
                card.item.title,
            ),
        )
    )
