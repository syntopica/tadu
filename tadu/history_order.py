"""Put the changes found to an item in history order."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.git_commit import GitCommit
    from tadu.history_event import HistoryEvent


def history_order(
    events: dict[str, tuple[GitCommit, HistoryEvent]], newer: dict[str, set[str]]
) -> list[HistoryEvent]:
    """The events (by commit) newest first, each after those it was found behind (`newer`).

    Among the events free to come next, the latest author date first, then the first found,
    so commits with the same date, as a rebase or a script makes them, keep their order.
    """
    found = list(events)
    waiting = {sha: set(later) & set(events) for sha, later in newer.items()}
    ordered: list[HistoryEvent] = []
    while waiting:
        free = [sha for sha, later in waiting.items() if not later]
        pick = max(
            free,
            key=lambda sha: (datetime.fromisoformat(events[sha][0].date), -found.index(sha)),
        )
        ordered.append(events[pick][1])
        del waiting[pick]
        for later in waiting.values():
            later.discard(pick)
    return ordered
