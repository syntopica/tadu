"""Reduce a prose line to what soft wrapping cannot change."""

from __future__ import annotations


def collapse_line(line: str) -> str:
    """The line's words joined by single spaces, keeping a trailing hard break as a newline."""
    words = " ".join(line.split())
    return words + "\n" if line.endswith("  ") else words
