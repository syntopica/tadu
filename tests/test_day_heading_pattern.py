from tadu.day_heading_pattern import DAY_HEADING_PATTERN


def test_day_but_not_month() -> None:
    assert DAY_HEADING_PATTERN.match("2026-10-19 - title")
    assert not DAY_HEADING_PATTERN.match("2026-10")
