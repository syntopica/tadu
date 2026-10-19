from datetime import date

from tadu.fenced_lines import fenced_lines
from tadu.log_view import LogView
from tadu.markdown_headings import markdown_headings
from tadu.place_in_year import place_in_year

DAY = date(2026, 10, 19)


def view(lines: list[str]) -> LogView:
    fenced = fenced_lines(lines)
    return LogView(lines, fenced, markdown_headings(lines, fenced))


def test_month_section_is_preferred_over_a_day_section() -> None:
    lines = ["## 2026", "", "### 2026-10-19 - x", "", "### 2026-10", "", "- [x] 2026-10-01 — a", ""]
    assert place_in_year(view(lines), 0, DAY, newest_first=True) == (6, [])


def test_day_section_is_used_without_a_month_section() -> None:
    lines = ["## 2026", "", "### 2026-10-19 - x", "", "Intro.", "", "### 2026-10-13 - y", ""]
    assert place_in_year(view(lines), 0, DAY, newest_first=False) == (5, [])


def test_missing_month_goes_first_when_newest_first() -> None:
    lines = ["## 2026", "", "### 2026-09", "", "- [x] 2026-09-01 — a", "", "## 2025", ""]
    assert place_in_year(view(lines), 0, DAY, newest_first=True) == (2, ["### 2026-10", ""])


def test_missing_month_goes_last_when_oldest_first() -> None:
    lines = ["## 2026", "", "### 2026-09", "", "- [x] 2026-09-01 — a", "", "## 2025", ""]
    assert place_in_year(view(lines), 0, DAY, newest_first=False) == (5, ["### 2026-10", ""])


def test_empty_year_takes_a_new_month() -> None:
    assert place_in_year(view(["## 2026", ""]), 0, DAY, newest_first=True) == (
        1,
        ["### 2026-10", ""],
    )
