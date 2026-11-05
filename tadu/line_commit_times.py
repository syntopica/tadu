"""Committer time of each line in `git blame --line-porcelain` output."""

from __future__ import annotations

from tadu.blame_header_pattern import BLAME_HEADER_PATTERN


def line_commit_times(output: str) -> dict[int, int]:
    """Map each 1-based final line number to the Unix time of the commit that last changed it."""
    times: dict[int, int] = {}
    line = 0
    for text in output.splitlines():
        if text.startswith("\t"):
            continue
        header = BLAME_HEADER_PATTERN.match(text)
        if header:
            line = int(header.group(1))
        elif text.startswith("committer-time "):
            times[line] = int(text.removeprefix("committer-time "))
    return times
