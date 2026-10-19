"""The heading text for a month section the log does not have yet."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.day_heading_pattern import DAY_HEADING_PATTERN

if TYPE_CHECKING:
    from datetime import date


def new_month_heading(
    headings: list[tuple[int, int, str]], year: range, level: int, day: date
) -> str:
    """The day, when every heading of `level` in the year is a day section; else the month."""
    texts = [text for index, depth, text in headings if depth == level and index in year]
    if texts and all(DAY_HEADING_PATTERN.match(text) for text in texts):
        return day.isoformat()
    return day.isoformat()[:7]
