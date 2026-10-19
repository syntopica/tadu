from tadu.year_heading_pattern import YEAR_HEADING_PATTERN


def test_year_or_month_only() -> None:
    assert YEAR_HEADING_PATTERN.match("2026")
    assert YEAR_HEADING_PATTERN.match("2026-10")
    assert not YEAR_HEADING_PATTERN.match("2026 notes")
