from datetime import date

from tadu.fresh_log_text import fresh_log_text
from tadu.log_marker_pattern import LOG_MARKER_PATTERN


def test_log_carries_a_marker_dated_today() -> None:
    text = fresh_log_text(date(2026, 10, 12))
    assert text.startswith("# TODO Log\n")
    markers = [line for line in text.splitlines() if LOG_MARKER_PATTERN.match(line)]
    assert markers == ["<!-- tadu:log v1 since 2026-10-12 -->"]
