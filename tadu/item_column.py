"""Board column of an item."""

from __future__ import annotations

COLUMNS = {"~": "in_progress", "!": "blocked", "x": "done", "-": "cancelled"}


def item_column(state: str, queue: str) -> str:
    """The column for a state marker; an open item is ready only when queued so."""
    if state == " ":
        return "ready" if queue == "ready" else "backlog"
    return COLUMNS[state]
