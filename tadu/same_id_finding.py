"""The finding for a task file whose id an earlier file already has."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.finding import Finding
from tadu.task_str import task_str
from tadu.todo_layout import CLOSED_DIR, OPEN_DIR

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.task_file import TaskFile


def same_id_finding(file: TaskFile, earlier: TaskFile, todo: Path) -> Finding:
    """J007 on the later file; an open copy with a closed one is a close that stopped halfway.

    `tadu close` writes the closed file first and deletes the open one second; run again, it
    finishes the close from the closed copy.
    """
    message = f"id also used by {earlier.path}"
    if earlier.path.parent == todo / OPEN_DIR and file.path.parent == todo / CLOSED_DIR:
        task_id = task_str(file.task, "id")
        message += (
            "; a close that stopped halfway leaves the task in open/ and closed/: "
            f"run tadu close --id {task_id} again to finish it"
        )
    return Finding("J007", "error", str(file.path), 0, message)
