"""The keys of the cards a deferred parent holds back."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

    from tadu.card import Card


def deferred_family(cards: tuple[Card, ...], today: date) -> frozenset[str]:
    """Keys of every card below a deferred parent, at any depth.

    A parent is deferred while its `defer_until` day is ahead, or for good when its kind is
    `later`. A parent that is not among the cards defers nothing.
    """
    # keys: task ids are unique and a task names one parent
    parent_of = {
        card.item.key: key
        for card in cards
        for kind, key in card.item.extras.relations
        if kind == "parent"
    }
    held = {
        card.item.key
        for card in cards
        if card.item.fields.kind == "later"
        or (card.item.extras.defer_until is not None and card.item.extras.defer_until > today)
    }
    below: set[str] = set()
    for key in parent_of:
        ancestor, seen = parent_of.get(key), {key}
        while ancestor is not None and ancestor not in seen:
            if ancestor in held:
                below.add(key)
                break
            seen.add(ancestor)
            ancestor = parent_of.get(ancestor)
    return frozenset(below)
