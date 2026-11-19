"""Serialise tadu writers of one repository's backlog."""

from __future__ import annotations

import contextlib
import hashlib
import os
from pathlib import Path
from typing import TYPE_CHECKING

from filelock import FileLock
from platformdirs import user_cache_dir

if TYPE_CHECKING:
    from collections.abc import Iterator


@contextlib.contextmanager
def backlog_lock(root: Path) -> Iterator[None]:
    """Hold an exclusive lock on the root's backlog until the block ends.

    On POSIX, an advisory flock on the root directory itself: nothing is written. Where
    there is no flock (Windows), filelock's lock on a file named after the root, in the
    user's own cache directory, so two agents on one machine still take turns.
    """
    try:
        import fcntl  # noqa: PLC0415 - POSIX only
    except ImportError:
        directory = Path(user_cache_dir("tadu", appauthor=False)) / "locks"
        # writes: the user's private lock directory, never inside the repository.
        directory.mkdir(parents=True, exist_ok=True)
        name = hashlib.sha256(str(root.resolve()).encode()).hexdigest()[:32]
        with FileLock(directory / f"{name}.lock"):
            yield
        return
    descriptor = os.open(root, os.O_RDONLY)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        os.close(descriptor)
