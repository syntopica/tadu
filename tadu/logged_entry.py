"""Find the log entry that already closed a backlog item."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.scan_items import scan_items

if TYPE_CHECKING:
    from tadu.backlog_item import BacklogItem


def logged_entry(todo: list[str], log: list[str], first: int) -> BacklogItem | None:
    """The first closed log entry with the `ID:` of the open item at line index `first`.

    One is there when a close wrote the entry and stopped before removing the item. An item
    without an `ID:` is never matched.
    """
    opened = scan_items(todo, "", "TODO.md", " ~!")
    uid = next((item.fields.id for item in opened if item.line == first + 1), None)
    if uid is None:
        return None
    closed = scan_items(log, "", "TODO_LOG.md", "x-")
    return next((entry for entry in closed if entry.fields.id == uid), None)
