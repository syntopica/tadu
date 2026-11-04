"""Field lines of one backlog item."""

from __future__ import annotations

from tadu.field_line_pattern import FIELD_LINE_PATTERN


def field_values(
    lines: list[str], fenced: list[bool], first: int, end: int
) -> list[tuple[int, str, str]]:
    """(index, name, stripped value) of each unfenced field line that starts a paragraph."""
    found: list[tuple[int, str, str]] = []
    for index in range(first + 1, end):
        match = FIELD_LINE_PATTERN.match(lines[index])
        if fenced[index] or match is None or lines[index - 1].strip():
            continue
        found.append((index, match.group(1), match.group(2).strip()))
    return found
