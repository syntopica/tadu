"""Where a top-level backlog item stops."""

from __future__ import annotations


def item_span_end(lines: list[str], first: int) -> int:
    """Index after the item's last indented line; an unindented line ends it."""
    end = first + 1
    for index in range(first + 1, len(lines)):
        line = lines[index]
        if not line.strip():
            continue
        if line[:1] not in (" ", "\t"):
            break
        end = index + 1
    return end
