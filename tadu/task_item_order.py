"""The order a task backlog's items are listed in by default."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from tadu.task_priorities import TASK_PRIORITIES

if TYPE_CHECKING:
    from tadu.backlog_item import BacklogItem

UNTRIAGED_RANK = TASK_PRIORITIES.index("untriaged")


def task_item_order(item: BacklogItem) -> tuple[bool, int, date, str]:
    """Open items first: most urgent, then nearest due date, then title; then closed ones, newest first.

    An item without a priority (untriaged) ranks between high and normal, as in TASK_PRIORITIES.
    """
    if item.state in "x-":
        return (True, 0, date.max - (item.day - date.min) if item.day else date.max, item.title)
    rank = item.fields.priority
    return (
        False,
        TASK_PRIORITIES.index(rank) if rank else UNTRIAGED_RANK,
        item.fields.due or date.max,
        item.title,
    )
