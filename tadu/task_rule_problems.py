"""The rules that tie a task's keys to its state."""

from __future__ import annotations

from tadu.task_field_kinds import TASK_CLOSING_KEYS
from tadu.task_states import OPEN_TASK_STATES

REQUIRED_WHEN = {"done": ("closed", "result", "evidence"), "cancelled": ("closed", "resolution")}


def task_rule_problems(task: dict[str, object]) -> tuple[str, ...]:
    """Messages for keys a state requires or forbids."""
    state = task.get("state")
    problems = [
        f"a {state} task needs {key}"
        for key in REQUIRED_WHEN.get(str(state), ())
        if key not in task
    ]
    if state == "blocked" and "blocker" not in task and "blocked_by" not in task:
        problems.append("a blocked task needs blocker or blocked_by")
    if state in OPEN_TASK_STATES:
        problems += [f"an open task cannot have {key}" for key in TASK_CLOSING_KEYS if key in task]
    if "duplicate_of" in task and state != "cancelled":
        problems.append("duplicate_of is only for a cancelled task")
    return tuple(problems)
