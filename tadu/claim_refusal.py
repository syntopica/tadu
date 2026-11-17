"""Decide whether a task may be claimed."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.task_states import OPEN_TASK_STATES
from tadu.task_str import task_str
from tadu.task_strings import task_strings
from tadu.waiting_on import waiting_on

if TYPE_CHECKING:
    from datetime import date
    from pathlib import Path


def claim_refusal(todo: Path, task: dict[str, object], who: str, today: date) -> str | None:
    """Why `who` may not take the task now, or None.

    Closed, blocked (by state or by an open blocked_by task), deferred, or in progress by
    someone else: taking over the last one needs --force, which the caller checks.
    """
    state = task_str(task, "state")
    waiting = waiting_on(todo, task)
    deferred = task_str(task, "defer_until")
    others = [person for person in task_strings(task, "assignees") if person != who]
    reasons = (
        (state not in OPEN_TASK_STATES, f"it is {state}"),
        (
            state == "blocked" or bool(waiting),
            f"it is blocked: {task_str(task, 'blocker') or ', '.join(waiting)}",
        ),
        (bool(deferred) and str(deferred) > today.isoformat(), f"it is deferred until {deferred}"),
        (
            state == "in_progress" and bool(others),
            f"it is in progress by {', '.join(others)} (use --force to take it over)",
        ),
    )
    return next((reason for applies, reason in reasons if applies), None)
