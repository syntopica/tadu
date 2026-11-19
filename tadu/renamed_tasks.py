"""Give the task files of a backlog the IDs an older migrate lost, in memory."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.renamed_task import renamed_task

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.task_file import TaskFile


def renamed_tasks(
    files: tuple[TaskFile, ...], mapping: dict[str, str]
) -> tuple[dict[str, tuple[TaskFile, dict[str, object]]], list[tuple[TaskFile, Path, None]]]:
    """Each task by its id after renaming, with its file; and the files a stopped run left.

    When a file renamed to its real ID meets the file already written under that ID, a run
    stopped between writing the new file and removing the old one: the one named by its id
    stays, and the other is listed, to be removed.
    """
    current: dict[str, tuple[TaskFile, dict[str, object]]] = {}
    stale: list[tuple[TaskFile, Path, None]] = []
    for file in files:
        task = renamed_task(file.task, mapping)
        task_id = str(task["id"])
        twin = current.get(task_id)
        if twin is None:
            # keys: one entry per id; a second file with it is handled below
            current[task_id] = (file, task)
            continue
        old, kept = (file, twin[0]) if file.task["id"] != task_id else (twin[0], file)
        stale.append((old, kept.path, None))
        # keys: the file named by this id replaces its stale twin
        current[task_id] = (kept, kept.task)
    return current, stale
