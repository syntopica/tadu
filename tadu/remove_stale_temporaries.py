"""Remove the temporary files killed writes left in one folder."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from tadu.clean_stale_temporaries import clean_stale_temporaries
from tadu.leftover_patterns import STALE_SECONDS

if TYPE_CHECKING:
    import re
    from pathlib import Path


def remove_stale_temporaries(folder: Path, pattern: re.Pattern[str]) -> None:
    """Delete the files of `folder` named like `pattern` that are older than STALE_SECONDS.

    A write renames its temporary file over the target within milliseconds, so an old one was
    left by a write that was killed (doctor's I001). The folder is scanned at most once per
    STALE_SECONDS, not for each of the thousands of files `tadu fmt` may write, while a
    long-running `tadu mcp` still cleans it again later.
    """
    # resolved: "." in two working directories of one long-running process are two folders
    clean_stale_temporaries(folder.resolve(), pattern, int(time.time() // STALE_SECONDS))
