"""Checks for the active backlog."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.closed_item_pattern import CLOSED_ITEM_PATTERN
from tadu.finding import Finding
from tadu.has_state_legend import has_state_legend
from tadu.read_text_exact import read_text_exact

if TYPE_CHECKING:
    from pathlib import Path


def check_todo_file(root: Path) -> tuple[Finding, ...]:
    """Report a missing backlog, a missing legend and closed items left active."""
    path = root / "TODO.md"
    if not path.is_file():
        return (Finding("T001", "error", str(path), 0, "no TODO.md"),)
    text = read_text_exact(path)
    if not text.strip():
        return (Finding("T004", "error", str(path), 0, "TODO.md is empty"),)
    findings: list[Finding] = []
    if not has_state_legend(text):
        findings.append(Finding("T002", "warning", str(path), 1, "no state legend"))
    for number, line in enumerate(text.splitlines(), start=1):
        if CLOSED_ITEM_PATTERN.match(line):
            findings.append(
                Finding(
                    "T003",
                    "error",
                    str(path),
                    number,
                    "closed item in the active backlog; move it to TODO_LOG.md",
                )
            )
    return tuple(findings)
