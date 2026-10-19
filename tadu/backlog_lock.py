"""Serialise tadu writers of one repository's backlog."""

from __future__ import annotations

import contextlib
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


@contextlib.contextmanager
def backlog_lock(root: Path) -> Iterator[None]:
    """Hold an exclusive advisory lock on the root directory; a no-op where flock is missing."""
    try:
        import fcntl  # noqa: PLC0415 - POSIX only; Windows runs unlocked
    except ImportError:  # pragma: no cover - not reachable on the POSIX test hosts
        yield
        return
    descriptor = os.open(root, os.O_RDONLY)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        os.close(descriptor)
