"""The L004 finding for a log without a dated tadu:log marker."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.finding import Finding

if TYPE_CHECKING:
    from pathlib import Path


def missing_log_marker_finding(path: Path) -> Finding:
    """L004: entries in this log are checked as warnings only."""
    message = "no <!-- tadu:log v1 since YYYY-MM-DD --> marker; entries are checked as warnings"
    return Finding("L004", "warning", str(path), 0, message)
