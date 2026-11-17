"""Find the repository a task file (format v2) belongs to."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.todo_layout import TASK_SUFFIX, TODO_CONFIG, TODO_DIR

if TYPE_CHECKING:
    from pathlib import Path


def task_file_root(path: Path) -> Path | None:
    """The directory holding the todo/ with tadu.json above a .json file, or None."""
    if path.suffix != TASK_SUFFIX:
        return None
    for directory in path.parents:
        if directory.name == TODO_DIR and (directory / TODO_CONFIG).is_file():
            return directory.parent
    return None
