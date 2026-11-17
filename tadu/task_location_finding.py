"""Check that a task file sits in the folder its state calls for."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.finding import Finding
from tadu.relative_posix import relative_posix
from tadu.task_states import OPEN_TASK_STATES
from tadu.task_str import task_str
from tadu.todo_layout import ARCHIVE_DIR, OPEN_DIR

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.task_file import TaskFile


def task_location_finding(file: TaskFile, todo: Path) -> Finding | None:
    """A J006 error for a task outside the folder its state calls for; None when it is in place.

    An open task belongs in open/; a closed one in closed/, or in archive/ under the year (or
    year and month) of its closed date.
    """
    state = task_str(file.task, "state")
    parts = tuple(relative_posix(file.path, todo).split("/"))
    closed = task_str(file.task, "closed") or ""
    message = None
    if state in OPEN_TASK_STATES and parts[0] != OPEN_DIR:
        message = f"{state} task outside {OPEN_DIR}/"
    elif state not in OPEN_TASK_STATES and parts[0] == OPEN_DIR:
        message = f"{state} task still in {OPEN_DIR}/"
    elif parts[0] == ARCHIVE_DIR and parts[1:-1] not in ((closed[:4],), (closed[:4], closed[5:7])):
        message = f"archived under {'/'.join(parts[1:-1])} but closed {closed}"
    return None if message is None else Finding("J006", "error", str(file.path), 0, message)
