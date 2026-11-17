"""An open item with a new state marker and, optionally, one more paragraph."""

from __future__ import annotations

from tadu.item_span_end import item_span_end


def marked_lines(lines: list[str], first: int, marker: str | None, note: str | None) -> list[str]:
    """The lines with the item at `first` set to `- [marker]` (None keeps it); the note ends the item."""
    changed = [*lines]
    if marker is not None:
        changed[first] = f"- [{marker}] {lines[first][6:]}"
    if note is not None:
        end = item_span_end(lines, first)
        changed[end:end] = ["", f"  {note.strip()}"]
    return changed
