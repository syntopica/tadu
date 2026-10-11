"""The fence run that starts a line, if any."""

from __future__ import annotations

from tadu.fence_line_pattern import FENCE_LINE_PATTERN


def fence_marker(line: str) -> str | None:
    """The run of backticks or tildes opening the line as a fence, else None."""
    match = FENCE_LINE_PATTERN.match(line)
    return match.group(1) if match else None
