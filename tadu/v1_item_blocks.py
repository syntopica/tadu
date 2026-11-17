"""Split a tadu v1 Markdown backlog into its top-level items."""

from __future__ import annotations

import re

from tadu.fenced_lines import fenced_lines
from tadu.item_state_pattern import ITEM_STATE_PATTERN
from tadu.lazy_item_span_end import lazy_item_span_end


def v1_item_blocks(lines: list[str]) -> tuple[tuple[tuple[str, ...], str | None], ...]:
    """Each unfenced top-level item's lines, with the `##` section it sits in.

    A `## YYYY` heading (a log year) is not a section.
    """
    fenced = fenced_lines(lines)
    blocks: list[tuple[tuple[str, ...], str | None]] = []
    section: str | None = None
    for index, line in enumerate(lines):
        if fenced[index]:
            continue
        if line.startswith("## "):
            heading = line[3:].strip()
            section = None if re.fullmatch(r"\d{4}", heading) else heading or None
        elif ITEM_STATE_PATTERN.match(line):
            blocks.append((tuple(lines[index : lazy_item_span_end(lines, index)]), section))
    return tuple(blocks)
