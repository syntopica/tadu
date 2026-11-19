"""Delete the temporary files killed writes left in one folder, at most once per period."""

from __future__ import annotations

import contextlib
import os
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

from tadu.leftover_patterns import STALE_SECONDS

if TYPE_CHECKING:
    import re


@lru_cache(maxsize=256)
def clean_stale_temporaries(folder: Path, pattern: re.Pattern[str], period: int) -> None:
    """Delete the files of `folder` named like `pattern` from before the previous period.

    `period` counts STALE_SECONDS since the epoch, so every file deleted is at least that
    old. Cached on it, so a folder is scanned once per period however many files are written
    to it. A file that cannot be checked or removed is left alone.
    """
    cutoff = (period - 1) * STALE_SECONDS
    try:
        entries = list(os.scandir(folder))
    except OSError:
        return
    for entry in entries:
        # path-name: only tadu's own temporary names, in the one folder it is cleaning
        if not pattern.fullmatch(entry.name):
            continue
        with contextlib.suppress(OSError):
            if entry.is_file(follow_symlinks=False) and entry.stat().st_mtime < cutoff:
                # writes: a temporary file of tadu's own, left by a write killed a minute ago or more
                Path(entry.path).unlink()
