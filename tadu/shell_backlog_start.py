"""Pick the directory a shell command's backlog write points at."""

from __future__ import annotations

from pathlib import Path

from tadu.close_root_word import close_root_word
from tadu.last_backlog_dir import last_backlog_dir
from tadu.shell_words import shell_words


def shell_backlog_start(command: str, start: Path) -> Path:
    """The `tadu close` root or the last backlog path's directory, relative to `start`."""
    words = shell_words(command)
    target = close_root_word(words) or last_backlog_dir(words)
    return start / Path(target).expanduser() if target else start
