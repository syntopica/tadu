"""The title of a backlog item: its first paragraph joined into one line."""

from __future__ import annotations

from tadu.field_like_pattern import FIELD_LIKE_PATTERN
from tadu.list_marker_pattern import LIST_MARKER_PATTERN


def item_title(lines: list[str], fenced: list[bool], first: int, text: str) -> str:
    """`text` plus each following indented line of the same paragraph, single-spaced."""
    parts = [text.strip()]
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
            break
        parts.append(stripped)
    return " ".join(parts)
