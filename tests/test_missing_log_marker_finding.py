from pathlib import Path

from tadu.missing_log_marker_finding import missing_log_marker_finding


def test_is_a_line_zero_l004_warning() -> None:
    finding = missing_log_marker_finding(Path("TODO_LOG.md"))
    assert (finding.code, finding.severity, finding.line) == ("L004", "warning", 0)
