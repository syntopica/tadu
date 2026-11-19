"""The recovery a task backlog has started and not finished."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.read_todo_config import read_todo_config
from tadu.task_file_error import TaskFileError

if TYPE_CHECKING:
    from pathlib import Path

PENDING_KEY = "x-format-1-recovering"


def pending_recovery(todo: Path) -> str | None:
    """The commit `tadu migrate --recover` started from and has not finished, as tadu.json says."""
    try:
        pending = read_todo_config(todo).get(PENDING_KEY)
    except TaskFileError:
        return None
    return pending if isinstance(pending, str) else None
