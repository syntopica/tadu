from datetime import date

from tadu.new_month_heading import new_month_heading

DAY = date(2026, 10, 19)


def test_month_heading_by_default() -> None:
    assert new_month_heading([], range(10), 3, DAY) == "2026-10"
    assert (
        new_month_heading([(2, 3, "2026-09"), (4, 3, "2026-08-01")], range(10), 3, DAY) == "2026-10"
    )


def test_day_heading_when_the_year_uses_day_sections() -> None:
    headings = [(2, 3, "2026-09-01 - a"), (5, 3, "2026-08-03"), (12, 3, "2025-12")]
    assert new_month_heading(headings, range(10), 3, DAY) == "2026-10-19"
