"""What closing a task means for the tasks that wait on it."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.load_task_files import load_task_files
from tadu.task_str import task_str
from tadu.task_strings import task_strings
from tadu.todo_layout import OPEN_DIR

if TYPE_CHECKING:
    from pathlib import Path


def waiting_report(todo: Path, closed: dict[str, object]) -> tuple[str, ...]:
    """One line per open task blocked by the closed one; none of them is changed.

    The agent decides what happens next: whether a freed task really moves to pending.
    """
    files, _ = load_task_files(todo, (OPEN_DIR,))
    own = task_str(closed, "id")
    open_ids = {task_str(file.task, "id") for file in files} - {own}
    lines: list[str] = []
    for file in files:
        task = file.task
        if own not in task_strings(task, "blocked_by"):
            continue
        name = f"{file.path.stem} {task_str(task, 'title')!r}"
        still = [target for target in task_strings(task, "blocked_by") if target in open_ids]
        if closed.get("state") == "cancelled":
            kept = task_str(closed, "duplicate_of") or task_str(closed, "superseded_by")
            hint = f" (block on {kept} instead?)" if kept else ""
            lines.append(
                f"  {name} waited on this task, which is cancelled, not done: review it{hint}"
            )
        elif still:
            lines.append(f"  {name} still waits on {', '.join(still)}")
        elif task_str(task, "blocker"):
            lines.append(
                f"  {name}: no task blocks it any more, but it is still blocked by: {task_str(task, 'blocker')}"
            )
        else:
            lines.append(f"  {name}: nothing blocks it now; decide whether it moves to pending")
    return tuple(lines)
