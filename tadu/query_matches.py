"""Decide whether a card satisfies a list query."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from tadu.priority_rank import priority_rank

if TYPE_CHECKING:
    from datetime import date

    from tadu.card import Card
    from tadu.list_query import ListQuery


def query_matches(card: Card, query: ListQuery, today: date) -> bool:
    """True when the card meets every criterion the query sets.

    --due-within N keeps items due on or before today + N, overdue ones included; --overdue
    keeps items due before today; --min-priority keeps that priority and more urgent ones.
    """
    item, extras = card.item, card.item.extras
    due = item.fields.due
    last_day = None
    if query.due_within is not None:
        last_day = today + timedelta(days=query.due_within)
    if query.overdue:
        last_day = today - timedelta(days=1)
    checks = (
        not query.categories or (extras.category or "") in query.categories,
        not query.types or (extras.task_type or "") in query.types,
        query.milestone in (None, extras.milestone),
        query.text is None or bool(query.text.search(f"{item.title}\n{item.text}")),
        last_day is None or (due is not None and due <= last_day),
        query.min_priority is None
        or (
            item.fields.priority is not None
            and priority_rank(item.fields.priority) <= priority_rank(query.min_priority)
        ),
    )
    return all(checks)
