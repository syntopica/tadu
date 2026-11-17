"""Sort keys for the list command's --sort option."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from tadu.priority_rank import priority_rank

if TYPE_CHECKING:
    from tadu.card import Card


def card_sort_key(card: Card, how: str) -> tuple[int, date, str]:
    """The key `how` sorts by; any unknown value keeps the read order (all keys equal).

    priority: most urgent, then nearest due; due: nearest due, then most urgent; closed: latest
    closing day first.
    """
    item = card.item
    rank, due = priority_rank(item.fields.priority), item.fields.due or date.max
    if how == "priority":
        return (rank, due, "")
    if how == "due":
        return (0, due, str(rank))
    if how == "closed":
        return (0, date.max - (item.day - date.min) if item.day else date.max, "")
    return (0, date.min, "")
