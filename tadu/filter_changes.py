"""Keep the changes `tadu changes` was asked for."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.filter_history import filter_history

if TYPE_CHECKING:
    from datetime import date

    from tadu.change_entry import ChangeEntry
    from tadu.history_filter import HistoryFilter


def filter_changes(
    entries: list[ChangeEntry], wanted: HistoryFilter, events: frozenset[str], today: date
) -> list[ChangeEntry]:
    """The changes of the events asked for (all when none), narrowed as item history is.

    Fields, days and author follow filter_history; the board filters with the same rules
    (filter-changes.js).
    """
    kept = [entry for entry in entries if not events or entry["event"] in events]
    return filter_history(kept, wanted, today)
