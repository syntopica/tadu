from tadu.fenced_lines import fenced_lines
from tadu.log_view import LogView
from tadu.markdown_headings import markdown_headings
from tadu.place_in_section import place_in_section

LINES = ["### 2026-10", "", "Intro.", "", "- [x] 2026-10-12 — a", "  - Evidence: e", "", "## 2025"]


def view() -> LogView:
    fenced = fenced_lines(LINES)
    return LogView(LINES, fenced, markdown_headings(LINES, fenced))


def test_newest_first_goes_before_the_first_entry() -> None:
    assert place_in_section(view(), range(1, 7), newest_first=True) == 4


def test_oldest_first_goes_after_the_last_text_line() -> None:
    assert place_in_section(view(), range(1, 7), newest_first=False) == 6


def test_section_without_entries_takes_it_at_its_end() -> None:
    assert place_in_section(view(), range(1, 4), newest_first=True) == 3
