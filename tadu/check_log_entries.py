"""Check each dated log entry for its proof line."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.entry_end import entry_end
from tadu.finding import Finding
from tadu.has_label_line import has_label_line
from tadu.is_legacy_entry import is_legacy_entry
from tadu.log_entry_pattern import LOG_ENTRY_PATTERN
from tadu.required_log_labels import REQUIRED_LOG_LABELS

if TYPE_CHECKING:
    from datetime import date
    from pathlib import Path


def check_log_entries(lines: list[str], path: Path, since: date | None) -> tuple[Finding, ...]:
    """Entries before since are skipped; without since, gaps are warnings."""
    severity = "error" if since else "warning"
    findings: list[Finding] = []
    for number, line in enumerate(lines, start=1):
        match = LOG_ENTRY_PATTERN.match(line)
        if match is None or (since is not None and is_legacy_entry(match.group(2), since)):
            continue
        code, label = REQUIRED_LOG_LABELS[match.group(1)]
        if not has_label_line(lines[number : entry_end(lines, number)], label):
            findings.append(
                Finding(code, severity, str(path), number, f"entry has no {label} line")
            )
    return tuple(findings)
