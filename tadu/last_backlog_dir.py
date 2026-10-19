"""Find the directory of the last backlog path in a command, its destination when it copies."""

from __future__ import annotations

from tadu.backlog_write_pattern import BACKLOG_PATH_PATTERN


def last_backlog_dir(words: list[str]) -> str | None:
    """The directory part of the last backlog path with one, or None."""
    found = [match for word in words for match in BACKLOG_PATH_PATTERN.findall(word)]
    return found[-1] if found else None
