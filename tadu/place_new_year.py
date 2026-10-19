"""Where a year section the log does not have yet goes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.first_heading import first_heading
from tadu.is_year_heading import is_year_heading
from tadu.trim_blank_tail import trim_blank_tail

if TYPE_CHECKING:
    from datetime import date


def place_new_year(
    lines: list[str], headings: list[tuple[int, int, str]], day: date, *, newest_first: bool
) -> tuple[int, list[str]]:
    """Before the first dated level-two section when newest first, else at the end."""
    heading = [f"## {day.year}", "", f"### {day.isoformat()[:7]}", ""]
    first = first_heading(headings, 2, range(len(lines)), is_year_heading)
    if newest_first and first is not None:
        return first, heading
    return trim_blank_tail(lines, len(lines), -1), heading
