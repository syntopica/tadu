"""Read every task file of a backlog."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.read_task_file import read_task_file
from tadu.task_file_error import TaskFileError
from tadu.task_file_paths import task_file_paths
from tadu.todo_layout import ARCHIVE_DIR, CLOSED_DIR, OPEN_DIR
from tadu.unreadable_file_error import UnreadableFileError

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.task_file import TaskFile


def load_task_files(
    todo: Path, folders: tuple[str, ...] = (OPEN_DIR, CLOSED_DIR, ARCHIVE_DIR)
) -> tuple[tuple[TaskFile, ...], tuple[tuple[Path, str], ...]]:
    """Task files from the folders asked for, in path order, and (path, reason) per unreadable one."""
    files: list[TaskFile] = []
    problems: list[tuple[Path, str]] = []
    for folder in folders:
        for path in task_file_paths(todo / folder):
            try:
                files.append(read_task_file(path))
            except (TaskFileError, UnreadableFileError) as error:
                problems.append((path, error.reason))
    return tuple(files), tuple(problems)
