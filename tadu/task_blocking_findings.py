"""Findings about a task's blocked_by relations and its state."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.finding import Finding
from tadu.open_blockers import open_blockers
from tadu.task_states import OPEN_TASK_STATES
from tadu.task_str import task_str
from tadu.task_strings import task_strings

if TYPE_CHECKING:
    from tadu.task_file import TaskFile


def task_blocking_findings(file: TaskFile, by_id: dict[str, TaskFile]) -> tuple[Finding, ...]:
    """Cancelled blockers, blocked tasks nothing blocks any more, and waiting tasks not marked blocked."""
    task, path = file.task, str(file.path)
    state = task_str(task, "state")
    if state not in OPEN_TASK_STATES or "blocked_by" not in task:
        return ()
    findings: list[Finding] = []
    for target in task_strings(task, "blocked_by"):
        other = by_id[target].task if target in by_id else {}
        if task_str(other, "state") == "cancelled":
            kept = task_str(other, "superseded_by") or task_str(other, "duplicate_of")
            hint = (
                f"; it was replaced by {kept}, block on that instead"
                if kept
                else "; decide whether this task still applies"
            )
            findings.append(
                Finding("J016", "warning", path, 0, f"blocked_by {target} was cancelled{hint}")
            )
    waiting = open_blockers(task, by_id)
    if state == "blocked" and not waiting and "blocker" not in task:
        message = "every blocked_by task is closed: decide whether it moves to pending"
        findings.append(Finding("J014", "warning", path, 0, message))
    if state != "blocked" and waiting:
        message = f"{state} but waits on open {', '.join(waiting)}; mark it blocked"
        findings.append(Finding("J015", "warning", path, 0, message))
    return tuple(findings)
