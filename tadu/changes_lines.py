"""The text of `tadu changes`."""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

from tadu.change_events import CHANGE_EVENTS
from tadu.change_line import change_line
from tadu.short_keys import short_keys

if TYPE_CHECKING:
    from datetime import date

    from tadu.change_entry import ChangeEntry


def changes_lines(entries: list[ChangeEntry], since: date, until: date) -> list[str]:
    """A heading with the days and the count, then a group per event, in CHANGE_EVENTS order.

    Each group says how many and who made them, most first (`Closed (3) · Ana 2, Bob 1`), then
    its changes newest first.
    """
    count = f"{len(entries)} change{'' if len(entries) == 1 else 's'}" if entries else "no change"
    lines = [f"tadu changes: {since.isoformat()} to {until.isoformat()} · {count}"]
    keys = short_keys(tuple(entry["key"] for entry in entries if entry["key"]))
    for event in CHANGE_EVENTS:
        group = [entry for entry in entries if entry["event"] == event]
        if not group:
            continue
        authors = Counter(entry["author"] or "" for entry in group)
        who = ", ".join(
            f"{name} {n}" for name, n in sorted(authors.items(), key=lambda a: (-a[1], a[0]))
        )
        lines += ["", f"{event.capitalize()} ({len(group)}) · {who}"]
        lines += [change_line(entry, keys.get(entry["key"] or "")) for entry in group]
    return lines
