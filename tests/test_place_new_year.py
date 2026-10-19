from datetime import date

from tadu.place_new_year import place_new_year

DAY = date(2026, 1, 2)
HEADING = ["## 2026", "", "### 2026-01", ""]
LINES = ["# Log", "", "## Notes", "", "## 2025", "", "- [x] 2025-12-01 — a", ""]
HEADINGS = [(0, 1, "Log"), (2, 2, "Notes"), (4, 2, "2025")]


def test_newest_first_goes_before_the_first_year() -> None:
    assert place_new_year(LINES, HEADINGS, DAY, newest_first=True) == (4, HEADING)


def test_oldest_first_goes_at_the_end() -> None:
    assert place_new_year(LINES, HEADINGS, DAY, newest_first=False) == (7, HEADING)


def test_log_without_years_takes_it_at_the_end() -> None:
    assert place_new_year(["# Log", ""], [(0, 1, "Log")], DAY, newest_first=True) == (1, HEADING)
