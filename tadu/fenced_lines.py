"""Which lines of a Markdown text belong to a fenced code block."""

from __future__ import annotations

from tadu.fence_marker import fence_marker


def fenced_lines(lines: list[str]) -> list[bool]:
    """True for each fence line and each line between an opening and its closing fence."""
    flags: list[bool] = []
    fence: str | None = None
    for line in lines:
        run = fence_marker(line)
        if fence is None and run:
            fence = run
            flags.append(True)
            continue
        flags.append(fence is not None)
        if fence is not None and run and run[0] == fence[0] and len(run) >= len(fence):
            fence = None if line.strip() == run else fence
    return flags
