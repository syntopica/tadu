"""Pick and order the cards a list-style command prints."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.card_matches import card_matches
from tadu.card_sort_key import card_sort_key
from tadu.query_matches import query_matches

if TYPE_CHECKING:
    from datetime import date

    from tadu.card import Card
    from tadu.card_filter import CardFilter
    from tadu.list_query import ListQuery


def select_cards(
    cards: tuple[Card, ...], card_filter: CardFilter, query: ListQuery, today: date
) -> tuple[Card, ...]:
    """The cards meeting the filter and the query, in the query's sort order (stable)."""
    kept = [c for c in cards if card_matches(c, card_filter) and query_matches(c, query, today)]
    return tuple(sorted(kept, key=lambda card: card_sort_key(card, query.sort)))
