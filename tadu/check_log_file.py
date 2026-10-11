"""Checks for the closed-work log."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from tadu.finding import Finding
from tadu.has_label_line import has_label_line
from tadu.is_legacy_entry import is_legacy_entry
from tadu.log_entry_pattern import LOG_ENTRY_PATTERN
from tadu.log_marker_pattern import LOG_MARKER_PATTERN
from tadu.required_log_labels import REQUIRED_LOG_LABELS


def check_log_file(root: Path) -> tuple[Finding, ...]:
    """Report a missing log and dated entries lacking their proof line."""
    path = root / "TODO_LOG.md"
    if not path.is_file():
        if (root / "TODO.md").is_file():
            return (Finding("L001", "warning", str(path), 0, "no TODO_LOG.md"),)
        return ()
    lines = path.read_text(encoding="utf-8").splitlines()
    findings: list[Finding] = []
    since = None
    for number, line in enumerate(lines, start=1):
        if match := LOG_MARKER_PATTERN.match(line):
            try:
                since = date.fromisoformat(match.group(1))
            except ValueError:
                findings.append(
                    Finding("L005", "error", str(path), number, "invalid tadu:log marker date")
                )
            break
    severity = "error" if since else "warning"
    if since is None:
        message = "no <!-- tadu:log v1 since YYYY-MM-DD --> marker; entries are checked as warnings"
        findings.append(Finding("L004", "warning", str(path), 0, message))
    starts = [
        (number, match.group(1), match.group(2))
        for number, line in enumerate(lines, start=1)
        if (match := LOG_ENTRY_PATTERN.match(line))
    ]
    for index, (number, state, stamp) in enumerate(starts):
        if since is not None and is_legacy_entry(stamp, since):
            continue
        end = starts[index + 1][0] - 1 if index + 1 < len(starts) else len(lines)
        code, label = REQUIRED_LOG_LABELS[state]
        if not has_label_line(lines[number:end], label):
            findings.append(
                Finding(code, severity, str(path), number, f"entry has no {label} line")
            )
    return tuple(findings)
