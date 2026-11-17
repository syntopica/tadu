"""Read one task file into its item cache payload."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.item_record import item_record
from tadu.read_task_file import read_task_file
from tadu.task_file_error import TaskFileError
from tadu.task_item import task_item
from tadu.unreadable_file_error import UnreadableFileError

if TYPE_CHECKING:
    from pathlib import Path


def fresh_cache_entry(path: Path, root: Path) -> list[object] | None:
    """[raw state, raw closed, item record], or None for an unreadable file (doctor reports it)."""
    try:
        file = read_task_file(path)
    except (TaskFileError, UnreadableFileError):
        return None
    return [file.task.get("state"), file.task.get("closed"), item_record(task_item(file, root))]
