"""One change of an item's history, as the commands and the board exchange it."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from tadu.history_change import HistoryChange
    from tadu.history_line import HistoryLine


class HistoryEntry(TypedDict):
    """A history event in JSON form, as `show --history --json` prints it.

    Its commit (None fields for uncommitted changes), whether it created the item, where the item
    is after it, what changed, and both texts of the item.
    """

    commit: str | None
    short: str | None
    parents: list[str]
    date: str | None
    author: str | None
    subject: str | None
    merge: bool
    created: bool
    path: str
    changes: list[HistoryChange]
    lines: list[HistoryLine]
    before_text: str | None
    after_text: str
