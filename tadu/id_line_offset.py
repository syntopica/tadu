"""Locate the ID field line inside one item's text."""

from __future__ import annotations

from tadu.fenced_lines import fenced_lines
from tadu.field_values import field_values


def id_line_offset(text: str, uid: str) -> int:
    """0-based line index of the unfenced ID field whose value is uid."""
    lines = text.splitlines()
    fields = field_values(lines, fenced_lines(lines), 0, len(lines))
    return next(index for index, name, value in fields if name == "ID" and value == uid)
