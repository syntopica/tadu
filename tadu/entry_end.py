"""Where a log entry's body stops."""

from __future__ import annotations

from tadu.entry_boundary_pattern import ENTRY_BOUNDARY_PATTERN


def entry_end(lines: list[str], first: int) -> int:
    """Index after the entry body that starts at `first`: the next item or heading, or the end."""
    for index in range(first, len(lines)):
        if ENTRY_BOUNDARY_PATTERN.match(lines[index]):
            return index
    return len(lines)
