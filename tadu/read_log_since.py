"""Read the legacy boundary date from a log's tadu:log marker."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from tadu.finding import Finding
from tadu.log_marker_pattern import LOG_MARKER_PATTERN
from tadu.missing_log_marker_finding import missing_log_marker_finding

if TYPE_CHECKING:
    from pathlib import Path


def read_log_since(lines: list[str], path: Path) -> tuple[date | None, tuple[Finding, ...]]:
    """The first marker's date, with L005 when it is invalid or L004 when no date exists."""
    for number, line in enumerate(lines, start=1):
        if match := LOG_MARKER_PATTERN.match(line):
            try:
                return date.fromisoformat(match.group(1)), ()
            except ValueError:
                invalid = Finding(
                    "L005", "error", str(path), number, "invalid tadu:log marker date"
                )
                return None, (invalid, missing_log_marker_finding(path))
    return None, (missing_log_marker_finding(path),)
