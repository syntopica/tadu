"""Where a task file belongs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.task_states import OPEN_TASK_STATES
from tadu.todo_layout import CLOSED_DIR, OPEN_DIR, TASK_SUFFIX

if TYPE_CHECKING:
    from pathlib import Path


def task_location(todo: Path, task: dict[str, object]) -> Path:
    """open/<id>.json while the task is open, closed/<id>.json once closed."""
    folder = OPEN_DIR if task.get("state") in OPEN_TASK_STATES else CLOSED_DIR
    return todo / folder / f"{task['id']}{TASK_SUFFIX}"
