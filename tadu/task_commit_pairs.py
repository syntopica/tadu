"""What one commit did to the tasks of a task backlog."""

from __future__ import annotations

from dataclasses import replace
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from tadu.task_todo_folder import task_todo_folder
from tadu.task_version_item import task_version_item
from tadu.task_versions import task_versions
from tadu.todo_layout import TASK_SUFFIX, TODO_DIR

if TYPE_CHECKING:
    from tadu.backlog_item import BacklogItem
    from tadu.change_source import ChangeSource
    from tadu.git_commit import GitCommit
    from tadu.git_file_change import GitFileChange


def task_commit_pairs(
    source: ChangeSource, commit: GitCommit
) -> list[tuple[BacklogItem | None, BacklogItem | None]]:
    """(before, after) for each task file of the backlog the commit changed, by task id.

    A move (git may record a delete and an add) is one pair. A merge reports a task only when it
    left it unlike every parent; a task that every parent had and the merge dropped was removed.
    """
    prefix, root, blobs = source.prefix, source.root, source.blobs
    todo = (PurePosixPath(source.backlog) / TODO_DIR).as_posix()
    by_task: dict[str, list[GitFileChange]] = {}
    for change in commit.files:
        path = PurePosixPath(change.path.removeprefix(prefix))
        # path-name: task files are named by their id, unique in one backlog
        if (
            path.suffix == TASK_SUFFIX
            and path.name.startswith("t-")
            and task_todo_folder(path.as_posix()) == todo
        ):
            # keys: one list per task id, to pair a move's delete and add
            by_task.setdefault(path.stem, []).append(change)
    pairs: list[tuple[BacklogItem | None, BacklogItem | None]] = []
    for changes in by_task.values():
        befores, after = task_versions(replace(commit, files=tuple(changes)), prefix, blobs)
        if (after is not None and after in befores) or (after is None and None in befores):
            continue
        before = next((version for version in befores if version), None)
        pairs.append(
            (
                task_version_item(root, *before) if before else None,
                task_version_item(root, *after) if after else None,
            )
        )
    return pairs
