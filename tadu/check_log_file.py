"""Checks for the closed-work log."""

from __future__ import annotations

import re
from pathlib import Path

from tadu.finding import Finding

ENTRY = re.compile(r"^- \[(x|-)\] \d{4}-\d{2}-\d{2} ")
REQUIRED = {"x": ("L002", "Evidence:"), "-": ("L003", "Resolution:")}


def check_log_file(root: Path) -> tuple[Finding, ...]:
    """Report a missing log and dated entries lacking their proof line."""
    path = root / "TODO_LOG.md"
    if not path.is_file():
        if (root / "TODO.md").is_file():
            return (Finding("L001", "warning", str(path), 0, "no TODO_LOG.md"),)
        return ()
    lines = path.read_text(encoding="utf-8").splitlines()
    starts = [
        (number, match.group(1))
        for number, line in enumerate(lines, start=1)
        if (match := ENTRY.match(line))
    ]
    findings: list[Finding] = []
    for index, (number, state) in enumerate(starts):
        end = starts[index + 1][0] - 1 if index + 1 < len(starts) else len(lines)
        code, label = REQUIRED[state]
        if not any(label in line for line in lines[number:end]):
            findings.append(Finding(code, "error", str(path), number, f"entry has no {label} line"))
    return tuple(findings)
