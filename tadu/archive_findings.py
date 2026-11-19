"""Findings about the archive folder as a whole."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.finding import Finding
from tadu.planned_archive_moves import planned_archive_moves
from tadu.relative_posix import relative_posix
from tadu.todo_layout import ARCHIVE_DIR, CLOSED_DIR, TODO_CONFIG

if TYPE_CHECKING:
    from datetime import date
    from pathlib import Path

    from tadu.task_file import TaskFile


def archive_findings(
    files: tuple[TaskFile, ...], todo: Path, config: dict[str, object], today: date
) -> tuple[Finding, ...]:
    """Archive layout and policy findings.

    A year that mixes YYYY/ and YYYY/MM/ folders, an archive without a policy, and the moves
    the policy calls for that were not made (a warning: closing tasks makes them due).
    """
    layouts: dict[str, set[int]] = {}
    for file in files:
        parts = relative_posix(file.path, todo).split("/")
        if parts[0] == ARCHIVE_DIR and len(parts) > 2:  # noqa: PLR2004 - archive/YYYY/<file>
            layouts.setdefault(parts[1], set()).add(len(parts))
    archive = str(todo / ARCHIVE_DIR)
    findings = [
        Finding(
            "J006",
            "error",
            f"{archive}/{year}",
            0,
            "mixes YYYY/ and YYYY/MM/ folders; run tadu archive --write",
        )
        for year, depths in sorted(layouts.items())
        if len(depths) > 1
    ]
    if layouts and "archive" not in config:
        message = "archive/ holds tasks but tadu.json has no archive policy"
        findings.append(Finding("C003", "warning", archive, 0, message))
    policy = config.get("archive")
    if isinstance(policy, dict):
        closed = tuple(file for file in files if file.path.parent == todo / CLOSED_DIR)
        archived = tuple(file for file in files if file.path.is_relative_to(todo / ARCHIVE_DIR))
        due = len(planned_archive_moves((closed, archived), todo, policy, today))
        message = (
            f"{due} task file(s) are due to move under the archive policy; run tadu archive --write"
        )
        findings += [Finding("C006", "warning", str(todo / TODO_CONFIG), 0, message)] if due else []
    return tuple(findings)
