"""Every place a task file can have been in."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from tadu.task_todo_folder import task_todo_folder
from tadu.todo_layout import ARCHIVE_DIR, CLOSED_DIR, OPEN_DIR

if TYPE_CHECKING:
    from datetime import date


def task_places(path: str, closed: date | None) -> tuple[str, ...]:
    """The task's file in open/, closed/, its archive year and month, and `path` where it is.

    The archive folders come from the `closed` day, for a closed task only: only a closed task
    is archived, and `closed` never changes once set. `path` is added when a hand put the file
    elsewhere. Exact paths, not a pattern: git then looks up one name per folder instead of matching
    every file of every commit, which keeps history fast in a backlog of thousands of tasks.
    Only a closed task is archived, and `closed` never changes once set.
    """
    todo = PurePosixPath(task_todo_folder(path))
    # path-name: the task id, which names its file in every folder
    name = PurePosixPath(path).name
    folders = [todo / OPEN_DIR, todo / CLOSED_DIR]
    if closed is not None:
        year = todo / ARCHIVE_DIR / f"{closed.year:04d}"
        folders += [year, year / f"{closed.month:02d}"]
    places = [(folder / name).as_posix() for folder in folders]
    return (*places, *([] if path in places else [path]))
