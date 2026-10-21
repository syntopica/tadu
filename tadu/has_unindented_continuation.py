"""Detect text that an indentation-only close could leave behind."""

from __future__ import annotations

from tadu.item_span_end import item_span_end
from tadu.single_line_start_pattern import SINGLE_LINE_START_PATTERN


def has_unindented_continuation(lines: list[str], first: int) -> bool:
    """Refuse an adjacent unindented tail outside a known checklist/heading boundary.

    CommonMark permits lazy paragraph continuation without indentation. Other
    unfamiliar blocks also require a manual move rather than guessing ownership.
    A blank separator, heading, comment or next checklist item is unambiguous.
    """
    end = item_span_end(lines, first)
    if end >= len(lines) or not lines[end].strip():
        return False
    return not (lines[end].startswith("- [") or SINGLE_LINE_START_PATTERN.match(lines[end]))
