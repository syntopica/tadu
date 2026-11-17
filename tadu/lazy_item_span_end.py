"""Where a legacy backlog item stops when its wrapped lines are not indented."""

from __future__ import annotations

from tadu.item_span_end import item_span_end
from tadu.item_state_pattern import ITEM_STATE_PATTERN
from tadu.list_marker_pattern import LIST_MARKER_PATTERN


def lazy_item_span_end(lines: list[str], first: int) -> int:
    """Like item_span_end, but an unindented line right after a text line keeps wrapping the item.

    A blank line, a heading, an item, a list marker or a fence ends the item as before.
    """
    end = item_span_end(lines, first)
    while end < len(lines) and lines[end].strip() and lines[end - 1].strip():
        line = lines[end]
        if (
            line.startswith(("#", "```", "~~~"))
            or ITEM_STATE_PATTERN.match(line)
            or LIST_MARKER_PATTERN.match(line)
        ):
            break
        end = item_span_end(lines, end)
    return end
