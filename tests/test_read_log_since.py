from datetime import date
from pathlib import Path

from tadu.read_log_since import read_log_since

PATH = Path("TODO_LOG.md")


def test_first_marker_date_is_returned() -> None:
    lines = ["# Log", "<!-- tadu:log v1 since 2026-10-12 -->"]
    assert read_log_since(lines, PATH) == (date(2026, 10, 12), ())


def test_no_marker_is_l004() -> None:
    since, findings = read_log_since(["# Log"], PATH)
    assert since is None
    assert [f.code for f in findings] == ["L004"]


def test_invalid_date_is_l005_then_l004() -> None:
    since, findings = read_log_since(["<!-- tadu:log v1 since 2026-13-40 -->"], PATH)
    assert since is None
    assert [(f.code, f.line) for f in findings] == [("L005", 1), ("L004", 0)]
