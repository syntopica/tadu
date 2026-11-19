"""Checks for files that a tadu write stopped halfway left in the repository."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.finding import Finding
from tadu.leftover_patterns import MIGRATION_STAGING, ROOT_TEMPORARY, TASK_TEMPORARY
from tadu.todo_layout import TODO_DIR

if TYPE_CHECKING:
    from pathlib import Path


def check_leftover_files(root: Path) -> tuple[Finding, ...]:
    """I001 for each temporary file, and for the migration folder, a stopped write left.

    tadu replaces a file by renaming a complete temporary copy over it, and `tadu migrate`
    builds `todo/` in a staging folder; a command killed before the rename leaves them
    behind. Nothing reads them, but `git add -A` would commit them.
    """
    found = [
        path
        for path in sorted(root.glob(".*.tmp"))
        # path-name: matches the temporary names tadu gives the files it writes at the root
        if ROOT_TEMPORARY.fullmatch(path.name)
    ] + [
        path
        for path in sorted((root / TODO_DIR).rglob(".*.tmp"))
        # path-name: matches the temporary names tadu gives the files it writes under todo/
        if TASK_TEMPORARY.fullmatch(path.name)
    ]
    message = (
        "a temporary file of a tadu write that stopped halfway; delete it, or let the next "
        "tadu write to its folder remove it"
    )
    findings = [Finding("I001", "warning", str(path), 0, message) for path in found]
    if (root / MIGRATION_STAGING).is_dir():
        staging = "tadu migrate stopped halfway; run it again, which starts over, or delete it"
        findings.append(Finding("I001", "warning", str(root / MIGRATION_STAGING), 0, staging))
    return tuple(findings)
