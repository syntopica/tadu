"""One change of a backlog, as `tadu changes` reports it."""

from __future__ import annotations

from tadu.history_entry import HistoryEntry


class ChangeEntry(HistoryEntry):
    """A history entry with the item it is about, for a backlog-wide view.

    Its repository and project, its key (the task id or `ID:`; None for an item without one),
    its title, and the kind of change: one of CHANGE_EVENTS.
    """

    repository: str
    project: str | None
    key: str | None
    title: str
    event: str
