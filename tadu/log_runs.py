"""Group the text of a format 1 log outside its dated entries into the entries it records."""

from __future__ import annotations

import re

from tadu.fenced_lines import fenced_lines
from tadu.item_state_pattern import ITEM_STATE_PATTERN
from tadu.unplaced_lines import unplaced_lines
from tadu.v1_layout import DATE_HEADING

HEADING_DAY = re.compile(r"#+\s+(\d{4}(?:-\d{2}(?:-\d{2})?)?)(?![\d-])")


def log_runs(lines: list[str]) -> list[tuple[int, list[str], str | None]]:
    """(first index, its lines verbatim, date) for each block of text outside the entries.

    A heading starts a block, and so does text after an entry or a date heading. The date
    is the one in the block's own heading, else the last `## YYYY`, `### YYYY-MM` or
    `### YYYY-MM-DD` heading above it: a year, a month or a day, or None.
    """
    fenced = fenced_lines(lines)
    unplaced = set(unplaced_lines(lines))
    runs: list[tuple[int, list[int], str | None]] = []
    period: str | None = None
    boundary = True
    for index, line in enumerate(lines):
        plain = not fenced[index]
        if index in unplaced:
            own = HEADING_DAY.match(line) if plain else None
            if boundary or (plain and line.startswith("#")):
                runs.append((index, [], own.group(1) if own else period))
            runs[-1][1].append(index)
            boundary = False
        elif plain and DATE_HEADING.fullmatch(line):
            period, boundary = line.lstrip("#").strip(), True
        elif plain and (ITEM_STATE_PATTERN.match(line) or line.startswith("## ")):
            boundary = True
    return [(first, lines[first : taken[-1] + 1], day) for first, taken, day in runs]
