"""Findings about the archive folder as a whole."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.finding import Finding
from tadu.relative_posix import relative_posix
from tadu.todo_layout import ARCHIVE_DIR

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.task_file import TaskFile


def archive_findings(
    files: tuple[TaskFile, ...], todo: Path, config: dict[str, object]
) -> tuple[Finding, ...]:
    """A year that mixes YYYY/ and YYYY/MM/ folders, and an archive without a policy."""
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
    return tuple(findings)
