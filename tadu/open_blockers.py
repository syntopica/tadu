"""Find which of a task's blocked_by targets are still open."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.task_states import OPEN_TASK_STATES
from tadu.task_str import task_str
from tadu.task_strings import task_strings

if TYPE_CHECKING:
    from tadu.task_file import TaskFile


def open_blockers(task: dict[str, object], by_id: dict[str, TaskFile]) -> tuple[str, ...]:
    """The blocked_by ids that are open, or unknown (an unknown task cannot be shown closed)."""
    return tuple(
        target
        for target in task_strings(task, "blocked_by")
        if target not in by_id or task_str(by_id[target].task, "state") in OPEN_TASK_STATES
    )
