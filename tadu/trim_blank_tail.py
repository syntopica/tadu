"""Step an insertion point back over blank lines."""

from __future__ import annotations


def trim_blank_tail(lines: list[str], index: int, floor: int) -> int:
    """The smallest index above `floor` such that every line from it up to `index` is blank."""
    while index > floor + 1 and not lines[index - 1].strip():
        index -= 1
    return index
