"""Remove a run of lines without leaving a doubled blank line behind."""

from __future__ import annotations


def remove_lines(lines: list[str], start: int, end: int) -> list[str]:
    """The lines without [start, end); a blank line on each side of the gap collapses to one."""
    kept = lines[:start] + lines[end:]
    if 0 < start < len(kept) and not kept[start - 1].strip() and not kept[start].strip():
        del kept[start]
    return kept
