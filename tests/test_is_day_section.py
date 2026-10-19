from datetime import date

from tadu.is_day_section import is_day_section

DAY = date(2026, 10, 19)


def test_heading_that_starts_with_the_day() -> None:
    assert is_day_section("2026-10-19 - tadu installed", DAY)
    assert is_day_section("2026-10-19", DAY)


def test_other_days_and_months_are_not_day_sections() -> None:
    assert not is_day_section("2026-10-13 - review", DAY)
    assert not is_day_section("2026-10", DAY)
