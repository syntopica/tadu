"""Find the lines of a format 1 file that tadu migrate carries into no task."""

from __future__ import annotations

from tadu.v1_layout import v1_layout


def unplaced_lines(lines: list[str]) -> list[int]:
    """Indices of the non-blank lines outside every item and past the header (see v1_layout)."""
    return list(v1_layout(lines).unplaced)
