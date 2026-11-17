"""Every finding for a task backlog (format v2)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.archive_findings import archive_findings
from tadu.checked_task_files import checked_task_files
from tadu.finding import Finding
from tadu.task_location_finding import task_location_finding
from tadu.task_set_findings import task_set_findings
from tadu.task_str import task_str
from tadu.task_vocabulary_findings import task_vocabulary_findings
from tadu.todo_config_findings import todo_config_findings
from tadu.todo_layout import TODO_DIR

if TYPE_CHECKING:
    from datetime import date
    from pathlib import Path

    from tadu.task_file import TaskFile


def task_backlog_findings(root: Path, today: date) -> tuple[Finding, ...]:
    """Configuration, unreadable files, each file, duplicate ids, then relations and the archive."""
    todo = root / TODO_DIR
    config_findings, config = todo_config_findings(todo)
    findings = list(config_findings)
    by_id: dict[str, TaskFile] = {}
    valid: list[TaskFile] = []
    for file, own in checked_task_files(todo):
        findings += own
        if file is None:
            continue
        task_id = task_str(file.task, "id") or ""
        if task_id in by_id:
            message = f"id also used by {by_id[task_id].path}"
            findings.append(Finding("J007", "error", str(file.path), 0, message))
        elif task_id:
            # keys: duplicate ids are reported by the check next to it
            by_id[task_id] = file
        if file.writable and not any(finding.code == "J003" for finding in own):
            valid.append(file)
            location = task_location_finding(file, todo)
            findings += [location] if location else []
            findings += task_vocabulary_findings(file, config, today)
    findings += task_set_findings(tuple(valid), by_id)
    findings += archive_findings(tuple(valid), todo, config)
    if (root / "TODO.md").is_file():
        message = "TODO.md is ignored next to a task backlog; remove it once migrated"
        findings.append(Finding("C004", "warning", str(root / "TODO.md"), 0, message))
    return tuple(findings)
