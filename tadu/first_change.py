"""Find, commit by commit, where an item got its text."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.git_log_commits import git_log_commits
from tadu.item_kept import item_kept

if TYPE_CHECKING:
    from tadu.git_commit import GitCommit
    from tadu.history_lead import HistoryLead
    from tadu.history_source import HistorySource


def first_change(source: HistorySource, lead: HistoryLead) -> GitCommit | None:
    """The newest commit behind the lead's tips that gave the item its text, read one by one.

    The slow way, for the change `git log -S` cannot see: one where the text was already there
    as part of something longer, such as lines dropped from the item's end. Only the files the
    item is in are read, and the walk stops at that commit.
    """
    where = frozenset({(lead.path, lead.text)})
    for commit in git_log_commits(source.root, (source.pathspec(lead.path),), lead.tips):
        if not item_kept(commit, source.prefix, where, source.blobs):
            return commit
    return None
