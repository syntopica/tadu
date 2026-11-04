"""Board column of an item."""

from __future__ import annotations

from tadu.state_columns import STATE_COLUMNS


def item_column(state: str, queue: str) -> str:
    """The column for a state marker; an open item is ready only when queued so."""
    if state == " ":
        return "ready" if queue == "ready" else "backlog"
    return STATE_COLUMNS[state]
