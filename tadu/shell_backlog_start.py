"""Pick the directory a shell command's backlog write points at."""

from __future__ import annotations

from pathlib import Path

from tadu.backlog_write_pattern import BACKLOG_PATH_PATTERN, TADU_CLOSE_ROOT_PATTERN


def shell_backlog_start(command: str, start: Path) -> Path:
    """The `tadu close` root or the first backlog path's directory, relative to `start`."""
    named = TADU_CLOSE_ROOT_PATTERN.search(command) or BACKLOG_PATH_PATTERN.search(command)
    target = named.group(1).strip("\"'") if named else ""
    return start / Path(target).expanduser() if target else start
