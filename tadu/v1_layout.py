"""Split a format 1 Markdown file: the one reading migrate, its completion and recovery share."""

from __future__ import annotations

import re

from tadu.fenced_lines import fenced_lines
from tadu.item_state_pattern import ITEM_STATE_PATTERN
from tadu.lazy_item_span_end import lazy_item_span_end
from tadu.v1_file_layout import V1FileLayout
from tadu.with_section_prose import with_section_prose

DATE_HEADING = re.compile(r"#{2,3} \d{4}(?:-\d{2}(?:-\d{2})?)?\s*")


def v1_layout(lines: list[str]) -> V1FileLayout:
    """The file's header, its unfenced top-level items and the text outside them.

    A `##` heading is a section unless it is a log year (`## YYYY`) or empty; the plain lines
    between it and its first item are the section's prose, which that item carries. Left out
    of the unplaced lines on purpose: the header, blank lines and the `## YYYY`, `### YYYY-MM`
    and `### YYYY-MM-DD` headings of a log. What remains, such as text after an item, a `###`
    subsection, a section without items or an old prose entry of a log, is unplaced.
    """
    fenced = fenced_lines(lines)
    items: list[tuple[int, tuple[str, ...], str | None]] = []
    unplaced: list[int] = []
    section: str | None = None
    waiting: list[int] = []  # heading and prose of a section whose first item is still ahead
    header_end, end = len(lines), 0
    for index, line in enumerate(lines):
        plain = not fenced[index]
        if index < end or not line.strip():
            continue
        if plain and ITEM_STATE_PATTERN.match(line):
            header_end, end = min(header_end, index), lazy_item_span_end(lines, index)
            prose = [lines[at].strip() for at in waiting[1:]]
            items.append((index, with_section_prose(tuple(lines[index:end]), prose), section))
            waiting = []
        elif plain and line.startswith("## "):
            header_end, heading = min(header_end, index), line[3:].strip()
            unplaced += waiting
            section = None if re.fullmatch(r"\d{4}", heading) else heading or None
            waiting = [index] if section else []
        elif index > header_end and waiting and plain and not line.startswith("#"):
            waiting.append(index)
        elif index > header_end and not (plain and DATE_HEADING.fullmatch(line)):
            unplaced.append(index)
    return V1FileLayout(tuple(items), tuple(sorted(unplaced + waiting)), header_end)
