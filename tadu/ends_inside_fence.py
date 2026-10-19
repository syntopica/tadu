"""Detect lines that open a fenced code block and never close it."""

from __future__ import annotations

from tadu.fence_marker import fence_marker


def ends_inside_fence(lines: list[str]) -> bool:
    """True when a fence opened in the lines is still open after the last one.

    A fence counts at up to three spaces past the item's two-space content indent;
    deeper, it is indented code.
    """
    fence: str | None = None
    for line in lines:
        run = fence_marker(line[1:] if line[:1] == "\t" else line.removeprefix("  "))
        if fence is None and run:
            fence = run
        elif fence is not None and run and run[0] == fence[0] and len(run) >= len(fence):
            fence = None if line.strip() == run else fence
    return fence is not None
