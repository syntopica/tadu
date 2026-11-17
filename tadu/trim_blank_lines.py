"""Trim the blank lines at both ends of a line list."""

from __future__ import annotations


def trim_blank_lines(lines: list[object]) -> list[object]:
    """Drop empty strings at the start and the end; blank lines inside are content."""
    start, end = 0, len(lines)
    while start < end and lines[start] == "":
        start += 1
    while end > start and lines[end - 1] == "":
        end -= 1
    return lines[start:end]
