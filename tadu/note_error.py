"""Validate one note paragraph of a new item."""

from __future__ import annotations

from tadu.fence_marker import fence_marker
from tadu.field_like_pattern import FIELD_LIKE_PATTERN
from tadu.list_marker_pattern import LIST_MARKER_PATTERN


def note_error(note: str) -> str | None:
    """Why the note would not stay a plain paragraph of the item, or None."""
    start = note.strip()
    if FIELD_LIKE_PATTERN.match(f"  {start}") or LIST_MARKER_PATTERN.match(start):
        return f"a note cannot start like a field or a list item: {start}"
    if fence_marker(start):
        return f"a note cannot open a code fence: {start}"
    return None
