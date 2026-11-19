"""Find the closed copy of an open task."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.read_task_file import read_task_file
from tadu.task_command_error import TaskCommandError
from tadu.task_file_error import TaskFileError
from tadu.todo_layout import CLOSED_DIR, OPEN_DIR
from tadu.unreadable_file_error import UnreadableFileError

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.task_file import TaskFile


def closed_copy(todo: Path, opened: TaskFile) -> TaskFile | None:
    """The closed/ file of a task in open/: there when a close stopped before deleting it."""
    if opened.path.parent != todo / OPEN_DIR:
        return None
    # path-name: a close moves a task file to closed/ under the same name
    path = todo / CLOSED_DIR / opened.path.name
    if not path.is_file():
        return None
    try:
        return read_task_file(path)
    except (TaskFileError, UnreadableFileError) as error:
        raise TaskCommandError(str(error)) from error
