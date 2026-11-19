"""Keep the part of an item's history a filter asks for."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from tadu.history_entry_day import history_entry_day

if TYPE_CHECKING:
    from datetime import date

    from tadu.history_entry import HistoryEntry
    from tadu.history_filter import HistoryFilter


def filter_history[E: HistoryEntry](
    entries: list[E], wanted: HistoryFilter, today: date
) -> list[E]:
    """The entries within the days and by the author asked for, in their order.

    With fields, only the changes and lines of those fields are kept, and an entry left with
    none is dropped: `state` keeps the commits that changed the state, showing that change. An
    uncommitted change has no author, so an author filter leaves it out. The board filters with
    the same rules (filter-history.js); names are compared lowercased, as JavaScript does.
    Entries with more keys, such as those of `tadu changes`, keep them.
    """
    since = wanted.since.isoformat() if wanted.since else ""
    until = wanted.until.isoformat() if wanted.until else "9999-12-31"
    author = (wanted.author or "").lower()
    kept: list[E] = []
    for entry in entries:
        day = history_entry_day(entry, today)
        by = (entry["author"] or "").lower()
        if not since <= day <= until or (author and author not in by):
            continue
        if not wanted.fields:
            kept.append(entry)
            continue
        changes = [change for change in entry["changes"] if change["field"] in wanted.fields]
        lines = [line for line in entry["lines"] if line["field"] in wanted.fields]
        if changes or lines:
            kept.append(cast("E", {**entry, "changes": changes, "lines": lines}))
    return kept
