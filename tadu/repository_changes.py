"""Every change git recorded to one backlog in a range of days."""

from __future__ import annotations

from datetime import timedelta
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from tadu.blob_reader import BlobReader
from tadu.change_event import change_event
from tadu.change_json import change_json
from tadu.change_source import ChangeSource
from tadu.git_checkout import git_checkout
from tadu.git_log_commits import git_log_commits
from tadu.history_source import HistorySource
from tadu.markdown_commit_pairs import markdown_commit_pairs
from tadu.markdown_commit_versions import markdown_commit_versions
from tadu.migration_commit import migration_commit
from tadu.task_commit_pairs import task_commit_pairs

if TYPE_CHECKING:
    from datetime import date

    from tadu.change_entry import ChangeEntry
    from tadu.change_repository import ChangeRepository

BACKLOG_PATHS = ("TODO.md", "TODO_LOG.md", "docs/todo-log", "todo")
# git stops at the commit date on this machine's clock; the days that count are the authors'.
SLACK = timedelta(days=2)


def repository_changes(repository: ChangeRepository, since: date, until: date) -> list[ChangeEntry]:
    """The changes of the commits authored from `since` to `until` (days included), newest first.

    One `git log` over both formats' files walks back to `since`; each commit is compared with
    its parents item by item (see markdown_commit_pairs and task_commit_pairs), so the cost
    follows the commits in the range, not the size of the backlog. The commit that migrated the
    backlog reports its tasks as migrated, not its Markdown items as removed. HistoryError when
    git cannot read the checkout.
    """
    root, backlog = repository.root, repository.backlog
    prefix, _ = git_checkout(root)
    folder = PurePosixPath(backlog)
    specs = tuple(HistorySource.pathspec((folder / name).as_posix()) for name in BACKLOG_PATHS)
    commits = git_log_commits(root, specs, since=since - SLACK)
    first, last = since.isoformat(), until.isoformat()
    entries: list[ChangeEntry] = []
    with BlobReader(root) as blobs:
        source = ChangeSource(
            repository.repository, repository.project, root, prefix, backlog, blobs
        )
        for commit in commits:
            if not first <= commit.date[:10] <= last:
                continue
            migrated = migration_commit(commit, prefix, backlog)
            pairs = task_commit_pairs(source, commit)
            if not migrated:
                pairs += markdown_commit_pairs(
                    markdown_commit_versions(source, commit), source.repository
                )
            events = (change_event(*pair, migrated=migrated) for pair in pairs)
            entries += [
                change_json(source, commit, pair, event)
                for pair, event in zip(pairs, events, strict=True)
            ]
    return entries
