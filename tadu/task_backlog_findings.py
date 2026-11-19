"""Every finding for a task backlog (format v2)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.archive_findings import archive_findings
from tadu.checked_task_files import checked_task_files
from tadu.migration_state_findings import migration_state_findings
from tadu.same_id_finding import same_id_finding
from tadu.task_contradiction_findings import task_contradiction_findings
from tadu.task_location_finding import task_location_finding
from tadu.task_set_findings import task_set_findings
from tadu.task_str import task_str
from tadu.task_vocabulary_findings import task_vocabulary_findings
from tadu.todo_config_findings import todo_config_findings
from tadu.todo_layout import TODO_DIR

if TYPE_CHECKING:
    from datetime import date
    from pathlib import Path

    from tadu.finding import Finding
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
            findings.append(same_id_finding(file, by_id[task_id], todo))
        elif task_id:
            # keys: duplicate ids are reported by the check next to it
            by_id[task_id] = file
        if file.writable and not any(finding.code == "J003" for finding in own):
            valid.append(file)
            location = task_location_finding(file, todo)
            findings += [location] if location else []
            findings += task_vocabulary_findings(file, config, today)
            findings += task_contradiction_findings(file, todo, today)
    findings += task_set_findings(tuple(valid), by_id)
    findings += archive_findings(tuple(valid), todo, config, today)
    findings += migration_state_findings(root, config)
    return tuple(findings)
