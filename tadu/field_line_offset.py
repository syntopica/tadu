"""Locate a field line inside one item's text."""

from __future__ import annotations

from tadu.fenced_lines import fenced_lines
from tadu.field_values import field_values


def field_line_offset(text: str, name: str) -> int:
    """0-based line index of the first unfenced field of that name read from the item."""
    lines = text.splitlines()
    fields = field_values(lines, fenced_lines(lines), 0, len(lines))
    return next(index for index, found, _ in fields if found == name)
