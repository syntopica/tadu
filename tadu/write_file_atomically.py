"""Replace a file's content so a failure never leaves it partly written."""

from __future__ import annotations

import stat
from typing import TYPE_CHECKING

from tadu.write_temp_sibling import write_temp_sibling

if TYPE_CHECKING:
    from pathlib import Path

from tadu.leftover_patterns import REPOSITORY_TEMPORARY
from tadu.remove_stale_temporaries import remove_stale_temporaries


def write_file_atomically(target: Path, text: str) -> None:
    """Write `text` to a sibling temp file, fsync it, then rename it over `target`.

    Temporary files that earlier writes were killed before renaming are removed afterwards.
    """
    mode = stat.S_IMODE(target.stat().st_mode) if target.exists() else 0o644
    temporary = write_temp_sibling(target, text, mode)
    try:
        temporary.replace(target)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    remove_stale_temporaries(target.parent, REPOSITORY_TEMPORARY)
