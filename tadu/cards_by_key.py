"""Find the cards a key given on the command line names."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.short_keys import MIN_LENGTH

if TYPE_CHECKING:
    from tadu.card import Card


def cards_by_key(cards: tuple[Card, ...], key: str) -> tuple[Card, ...]:
    """Cards whose key is `key`, else whose task id starts with it (10 characters or more).

    More than one card means the key is ambiguous; the caller lists them instead of guessing.
    """
    exact = tuple(card for card in cards if card.item.key == key)
    if exact or not key.startswith("t-") or len(key) < MIN_LENGTH:
        return exact
    return tuple(card for card in cards if card.item.key.startswith(key))
