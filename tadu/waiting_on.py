"""Find which tasks a task still waits on."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.locate_task import locate_task
from tadu.task_command_error import TaskCommandError
from tadu.task_states import OPEN_TASK_STATES
from tadu.task_str import task_str
from tadu.task_strings import task_strings

if TYPE_CHECKING:
    from pathlib import Path


def waiting_on(todo: Path, task: dict[str, object]) -> tuple[str, ...]:
    """The blocked_by ids that are still open, or cannot be found (a missing task is not closed)."""
    waiting: list[str] = []
    for target in task_strings(task, "blocked_by"):
        try:
            state = task_str(locate_task(todo, target).task, "state")
        except TaskCommandError:
            state = None
        if state is None or state in OPEN_TASK_STATES:
            waiting.append(target)
    return tuple(waiting)
