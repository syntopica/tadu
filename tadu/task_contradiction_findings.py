"""Warnings for keys of an open task that contradict each other or its state."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.field_contradictions import field_contradictions
from tadu.field_names import TASK_NAMES
from tadu.finding import Finding
from tadu.task_item import task_item
from tadu.task_states import OPEN_TASK_STATES
from tadu.task_str import task_str

if TYPE_CHECKING:
    from datetime import date
    from pathlib import Path

    from tadu.task_file import TaskFile


def task_contradiction_findings(file: TaskFile, todo: Path, today: date) -> list[Finding]:
    """J023 for each contradiction doctor's F004 reports in format 1, worded with the task's keys.

    `defer_until` or `check_on` after `due`, in progress while `defer_until` is ahead or
    `kind` is later, and `queue` ready on a waiting or later task. A closed task is not judged.
    """
    if task_str(file.task, "state") not in OPEN_TASK_STATES:
        return []
    return [
        Finding("J023", "warning", str(file.path), 0, message)
        for _, message in field_contradictions(task_item(file, todo.parent), today, TASK_NAMES)
    ]
