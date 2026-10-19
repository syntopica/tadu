"""Where an entry goes inside the year section that exists for it."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.first_heading import first_heading
from tadu.is_day_section import is_day_section
from tadu.new_month_heading import new_month_heading
from tadu.place_in_section import place_in_section
from tadu.section_stop import section_stop
from tadu.trim_blank_tail import trim_blank_tail

if TYPE_CHECKING:
    from datetime import date

    from tadu.log_view import LogView


def place_in_year(
    view: LogView, year: int, day: date, *, newest_first: bool
) -> tuple[int, list[str]]:
    """Into the month section, else that day's section, else a new section in the year."""
    body = range(year + 1, section_stop(view.headings, year, 2, len(view.lines)))
    month = day.isoformat()[:7]
    section = first_heading(view.headings, 3, body, lambda text: text == month)
    if section is None:
        section = first_heading(view.headings, 3, body, lambda text: is_day_section(text, day))
    if section is not None:
        span = range(section + 1, section_stop(view.headings, section, 3, body.stop))
        return place_in_section(view, span, newest_first=newest_first), []
    heading = [f"### {new_month_heading(view.headings, body, 3, day)}", ""]
    first = first_heading(view.headings, 3, body, lambda _text: True)
    if newest_first and first is not None:
        return first, heading
    return trim_blank_tail(view.lines, body.stop, year), heading
