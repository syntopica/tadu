"""Findings about one task file on its own."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from tadu.canonical_task_text import canonical_task_text
from tadu.finding import Finding
from tadu.secret_lines import secret_lines
from tadu.task_format_version import TASK_FORMAT_VERSION
from tadu.task_id_pattern import TASK_ID_PATTERN
from tadu.task_problems import task_problems
from tadu.task_str import task_str
from tadu.task_strings import task_strings

if TYPE_CHECKING:
    from tadu.task_file import TaskFile

LOST_ID = re.compile(f"ID: ({TASK_ID_PATTERN.pattern.strip('^$')})")


def task_file_findings(file: TaskFile) -> tuple[Finding, ...]:
    """Newer version, secrets, schema problems, then form, file name and lost ID of a valid task.

    Returns the findings and stops early: an invalid task is not judged on its form.
    """
    path = str(file.path)
    if not file.writable:
        message = (
            f"written by tadu format {file.task['tadu']}; this tool knows "
            f"{TASK_FORMAT_VERSION} and will not rewrite it"
        )
        return (Finding("J002", "warning", path, 0, message),)
    findings = [
        Finding(
            "J017",
            "warning",
            path,
            n,
            f"looks like {kind}; do not commit secrets (value not shown)",
        )
        for n, kind in secret_lines(file.text)
    ]
    problems = task_problems(file.task)
    findings += [Finding("J003", "error", path, 0, problem) for problem in problems]
    if problems:
        return tuple(findings)
    if file.text != canonical_task_text(file.task):
        findings.append(Finding("J004", "warning", path, 0, "not in canonical form; run tadu fmt"))
    task_id = task_str(file.task, "id")
    if file.path.stem != task_id:
        findings.append(Finding("J005", "error", path, 0, f"file name does not match id {task_id}"))
    for note in task_strings(file.task, "notes"):
        lost = LOST_ID.fullmatch(note)
        if lost and lost.group(1) != task_id:
            message = (
                f"notes hold `{note}`, an ID that an older tadu's migrate lost; "
                "tadu migrate --recover gives it back"
            )
            findings.append(Finding("J022", "warning", path, 0, message))
    return tuple(findings)
