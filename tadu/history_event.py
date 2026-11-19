"""One change to an item, found in git."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.backlog_item import BacklogItem
    from tadu.git_commit import GitCommit


@dataclass(frozen=True)
class HistoryEvent:
    """The item before and after one commit, or the uncommitted changes when commit is None.

    `before` is None when the commit created the item. For a merge that left the item unlike
    every parent, `before` is the item in the first parent that had it.
    """

    commit: GitCommit | None
    before: BacklogItem | None
    after: BacklogItem
