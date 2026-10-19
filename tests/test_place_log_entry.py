from datetime import date

from tadu.fenced_lines import fenced_lines
from tadu.log_view import LogView
from tadu.markdown_headings import markdown_headings
from tadu.place_log_entry import place_log_entry


def view(lines: list[str]) -> LogView:
    fenced = fenced_lines(lines)
    return LogView(lines, fenced, markdown_headings(lines, fenced))


def test_missing_year_is_created() -> None:
    index, headings = place_log_entry(view(["# Log", ""]), date(2026, 3, 1), newest_first=False)
    assert (index, headings[0]) == (1, "## 2026")


def test_existing_year_is_used() -> None:
    lines = ["## 2026", "", "### 2026-03", "", "- [x] 2026-03-01 — a", ""]
    assert place_log_entry(view(lines), date(2026, 3, 5), newest_first=False) == (5, [])
