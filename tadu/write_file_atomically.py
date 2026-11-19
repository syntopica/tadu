"""Replace a file's content so a failure never leaves it partly written."""

from __future__ import annotations

import stat
from typing import TYPE_CHECKING

from tadu.write_temp_sibling import write_temp_sibling

if TYPE_CHECKING:
    from pathlib import Path


def write_file_atomically(target: Path, text: str) -> None:
    """Write `text` to a sibling temp file, fsync it, then rename it over `target`."""
    mode = stat.S_IMODE(target.stat().st_mode) if target.exists() else 0o644
    temporary = write_temp_sibling(target, text, mode)
    try:
        temporary.replace(target)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
