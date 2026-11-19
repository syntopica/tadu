"""Where the title paragraph of a backlog item stops."""

from __future__ import annotations

from tadu.field_like_pattern import FIELD_LIKE_PATTERN
from tadu.list_marker_pattern import LIST_MARKER_PATTERN


def title_end(lines: list[str], fenced: list[bool], first: int) -> int:
    """Index after the last line of the item's first paragraph, the item line included.

    The paragraph stops at a blank, unindented or fenced line, a nested list item or a field line.
    """
    for index in range(first + 1, len(lines)):
        line = lines[index].rstrip("\r")
        stripped = line.strip()
        if (
            not stripped
            or line[0] not in " \t"
            or fenced[index]
            or LIST_MARKER_PATTERN.match(stripped)
            or FIELD_LIKE_PATTERN.match(line)
        ):
            return index
    return len(lines)
