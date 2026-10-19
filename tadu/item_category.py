"""The backlog section an item sits in."""

from __future__ import annotations


def item_category(headings: list[tuple[int, int, str]], index: int, level: int) -> str | None:
    """The text of the nearest non-empty heading of `level` above line `index`, or None."""
    above = [text for line, depth, text in headings if line < index and depth == level and text]
    return above[-1] if above else None
