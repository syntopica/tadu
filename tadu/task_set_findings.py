"""Findings that need every task of the backlog at once."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.blocked_by_cycles import blocked_by_cycles
from tadu.finding import Finding
from tadu.task_blocking_findings import task_blocking_findings
from tadu.task_reference_findings import task_reference_findings

if TYPE_CHECKING:
    from tadu.task_file import TaskFile


def task_set_findings(
    valid: tuple[TaskFile, ...], by_id: dict[str, TaskFile]
) -> tuple[Finding, ...]:
    """Relation targets, blocked_by states and cycles, for the tasks that passed their own checks."""
    findings: list[Finding] = []
    for file in valid:
        findings += task_reference_findings(file, by_id)
        findings += task_blocking_findings(file, by_id)
    # keys: duplicate ids are reported by the backlog check
    valid_ids = {str(file.task["id"]): file for file in valid}
    for cycle in blocked_by_cycles(valid_ids):
        message = "blocked_by cycle: " + " -> ".join(cycle)
        findings.append(Finding("J013", "error", str(valid_ids[cycle[0]].path), 0, message))
    return tuple(findings)
