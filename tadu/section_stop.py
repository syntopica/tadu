"""Where a Markdown section stops."""

from __future__ import annotations


def section_stop(headings: list[tuple[int, int, str]], start: int, level: int, stop: int) -> int:
    """Line index of the next heading after `start` at `level` or higher, before `stop`."""
    for index, depth, _text in headings:
        if start < index < stop and depth <= level:
            return index
    return stop
