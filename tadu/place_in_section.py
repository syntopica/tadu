"""Where a new entry goes inside an existing month or day section."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.log_entry_pattern import LOG_ENTRY_PATTERN
from tadu.trim_blank_tail import trim_blank_tail

if TYPE_CHECKING:
    from tadu.log_view import LogView


def place_in_section(view: LogView, section: range, *, newest_first: bool) -> int:
    """Before the section's first entry when newest first, else after its last line of text."""
    if newest_first:
        for index in section:
            if not view.fenced[index] and LOG_ENTRY_PATTERN.match(view.lines[index]):
                return index
    return trim_blank_tail(view.lines, section.stop, section.start - 1)
