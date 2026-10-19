"""Decide where a closed entry goes in the log and which headings it needs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.first_heading import first_heading
from tadu.place_in_year import place_in_year
from tadu.place_new_year import place_new_year

if TYPE_CHECKING:
    from datetime import date

    from tadu.log_view import LogView


def place_log_entry(view: LogView, day: date, *, newest_first: bool) -> tuple[int, list[str]]:
    """The insertion index and the headings to put before the entry there."""
    everything = range(len(view.lines))
    year = first_heading(view.headings, 2, everything, lambda text: text == str(day.year))
    if year is None:
        return place_new_year(view.lines, view.headings, day, newest_first=newest_first)
    return place_in_year(view, year, day, newest_first=newest_first)
