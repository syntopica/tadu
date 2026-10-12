"""Compare two texts as a Markdown formatter would leave them."""

from __future__ import annotations


def same_ignoring_blank_lines(left: str, right: str) -> bool:
    """True when the texts differ only in blank lines, so a formatter's spacing is not drift."""
    return [line for line in left.splitlines() if line.strip()] == [
        line for line in right.splitlines() if line.strip()
    ]
