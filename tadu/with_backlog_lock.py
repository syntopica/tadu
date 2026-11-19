"""Run a command that changes a backlog under the repository's lock."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from tadu.backlog_lock import backlog_lock

if TYPE_CHECKING:
    from collections.abc import Callable


def with_backlog_lock(root: str, run: Callable[[], int]) -> int:
    """`run()` while holding the lock every tadu writer of the repository at `root` takes.

    Format 1 commands take it around their read and write; this gives a task backlog's
    commands the same, so two of them never interleave. A root that is not a directory runs
    unlocked: the command itself says what is wrong with it.
    """
    if not Path(root).is_dir():
        return run()
    with backlog_lock(Path(root)):
        return run()
