"""Findings about where a task's relations point."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.finding import Finding
from tadu.task_relations import task_relations
from tadu.task_str import task_str

if TYPE_CHECKING:
    from tadu.task_file import TaskFile


def task_reference_findings(file: TaskFile, by_id: dict[str, TaskFile]) -> tuple[Finding, ...]:
    """Relations to the task itself or to a missing task, and duplicates of duplicates."""
    path, own = str(file.path), task_str(file.task, "id")
    findings: list[Finding] = []
    for key, target in task_relations(file.task):
        if target == own:
            findings.append(Finding("J020", "error", path, 0, f"{key} points to the task itself"))
        elif target not in by_id:
            message = f"{key} {target} is not a task of this backlog"
            findings.append(Finding("J012", "error", path, 0, message))
    kept = task_str(file.task, "duplicate_of")
    further = task_str(by_id[kept].task, "duplicate_of") if kept in by_id else None
    if further:
        message = (
            f"duplicate_of {kept}, itself a duplicate of {further}: point to the task that was kept"
        )
        findings.append(Finding("J021", "warning", path, 0, message))
    return tuple(findings)
