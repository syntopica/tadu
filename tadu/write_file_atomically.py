"""Replace a file's content so a failure never leaves it partly written."""

from __future__ import annotations

import os
import stat
import tempfile
from pathlib import Path

from tadu.leftover_patterns import REPOSITORY_TEMPORARY
from tadu.remove_stale_temporaries import remove_stale_temporaries


def write_file_atomically(target: Path, text: str) -> None:
    """Write `text` to a sibling temp file, fsync it, then rename it over `target`.

    Temporary files that earlier writes were killed before renaming are removed afterwards.
    """
    mode = stat.S_IMODE(target.stat().st_mode) if target.exists() else 0o644
    # path-name: only names the temporary file beside the target.
    descriptor, name = tempfile.mkstemp(dir=target.parent, prefix=f".{target.name}.", suffix=".tmp")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        Path(name).chmod(mode)
        Path(name).replace(target)
    except BaseException:
        Path(name).unlink(missing_ok=True)
        raise
    remove_stale_temporaries(target.parent, REPOSITORY_TEMPORARY)
