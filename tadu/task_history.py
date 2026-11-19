"""The history of one task file (format v2)."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from tadu.blob_reader import BlobReader
from tadu.git_log_commits import git_log_commits
from tadu.history_event import HistoryEvent
from tadu.history_source import HistorySource
from tadu.migration_history import migration_history
from tadu.task_places import task_places
from tadu.task_todo_folder import task_todo_folder
from tadu.task_version_item import task_version_item
from tadu.task_versions import Version, task_versions
from tadu.working_text import working_text

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.backlog_item import BacklogItem
    from tadu.git_commit import GitCommit


def task_history(
    root: Path, prefix: str, item: BacklogItem, repository: str
) -> tuple[HistoryEvent, ...]:
    """Each change to the task, newest first (uncommitted ones on top), back to its creation.

    One `git log` over the places the file can have been in (see task_places) finds every
    commit, in open/, closed/ or archive/, so moving the file between them is a change of its
    `file`. A task that `tadu migrate` created goes on with its Markdown item's history (see
    migration_history).
    """
    places = task_places(item.path, item.day)
    with BlobReader(root) as blobs:
        commits = git_log_commits(root, tuple(HistorySource.pathspec(place) for place in places))
        versions = [(commit, *task_versions(commit, prefix, blobs)) for commit in commits]
        head = next((after for _, _, after in versions if after), None)
        working = (item.path, working_text(root / item.path))
        found: list[tuple[GitCommit | None, Version, tuple[str, str]]] = []
        found += [(None, head, working)] if working != head else []
        found += [
            (commit, next((b for b in befores if b), None), after)
            for commit, befores, after in versions
            if after is not None and after not in befores
        ]
        events = [
            HistoryEvent(
                commit,
                task_version_item(root, *before) if before else None,
                task_version_item(root, *after),
            )
            for commit, before, after in found
        ]
        source = HistorySource(root, prefix, (), repository, blobs)
        backlog = PurePosixPath(task_todo_folder(item.path)).parent.as_posix()
        oldest = migration_history(source, events[-1], backlog)
    return (*events[:-1], *oldest)
