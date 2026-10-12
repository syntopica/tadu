from datetime import date
from pathlib import Path

from tadu.check_log_entries import check_log_entries

PATH = Path("TODO_LOG.md")
LINES = [
    "- [x] 2026-10-01 — **A:** Old, no proof.",
    "",
    "- [x] 2026-10-12 — **A:** New, proved.",
    "  - Evidence: `pytest`.",
    "",
    "- [x] 2026-10-13 — **A:** New, no proof.",
]


def test_without_since_every_gap_is_a_warning() -> None:
    findings = check_log_entries(LINES, PATH, None)
    assert [(f.line, f.severity) for f in findings] == [(1, "warning"), (6, "warning")]


def test_with_since_legacy_entries_are_skipped_and_gaps_are_errors() -> None:
    findings = check_log_entries(LINES, PATH, date(2026, 10, 12))
    assert [(f.line, f.severity) for f in findings] == [(6, "error")]
