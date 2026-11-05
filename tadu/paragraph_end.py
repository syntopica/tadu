"""Where a Markdown paragraph stops."""

from __future__ import annotations


def paragraph_end(lines: list[str], fenced: list[bool], start: int, end: int) -> int:
    """Index after the paragraph starting at start: a blank or fenced line, or end, stops it."""
    stop = start + 1
    while stop < end and lines[stop].strip() and not fenced[stop]:
        stop += 1
    return stop
