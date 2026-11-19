"""The day a history entry happened."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

    from tadu.history_entry import HistoryEntry


def history_entry_day(entry: HistoryEntry, today: date) -> str:
    """`YYYY-MM-DD` of the commit's author date, as written in it; today for uncommitted changes."""
    return entry["date"][:10] if entry["date"] else today.isoformat()
