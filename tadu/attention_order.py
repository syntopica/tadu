"""Sort key that puts the most pressing card first."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from tadu.priorities import PRIORITIES

if TYPE_CHECKING:
    from tadu.card import Card

COLUMN_RANK = {"in_progress": 0, "ready": 1, "backlog": 2}


def attention_order(card: Card) -> tuple[int, date, int]:
    """Priority (none last), the earlier of `Due:` and `Check on:`, then the column.

    Started work comes before ready work, and ready before the backlog.
    """
    fields = card.item.fields
    rank = PRIORITIES.index(fields.priority) if fields.priority else len(PRIORITIES)
    day = min((d for d in (fields.due, fields.check_on) if d is not None), default=date.max)
    return rank, day, COLUMN_RANK.get(card.column, len(COLUMN_RANK))
