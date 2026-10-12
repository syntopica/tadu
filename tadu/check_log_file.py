"""Checks for the closed-work log."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.check_log_entries import check_log_entries
from tadu.finding import Finding
from tadu.read_log_since import read_log_since
from tadu.read_text_exact import read_text_exact

if TYPE_CHECKING:
    from pathlib import Path


def check_log_file(root: Path) -> tuple[Finding, ...]:
    """Report a missing log and dated entries lacking their proof line."""
    path = root / "TODO_LOG.md"
    if not path.is_file():
        if (root / "TODO.md").is_file():
            return (Finding("L001", "warning", str(path), 0, "no TODO_LOG.md"),)
        return ()
    text = read_text_exact(path)
    if not text.strip():
        return (Finding("L006", "warning", str(path), 0, "TODO_LOG.md is empty"),)
    lines = text.splitlines()
    since, marker_findings = read_log_since(lines, path)
    return marker_findings + check_log_entries(lines, path, since)
