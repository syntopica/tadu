"""Write a file's next content beside it, durably, before it takes the file's place."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


def write_temp_sibling(target: Path, text: str, mode: int) -> Path:
    """A temporary file in the target's directory holding `text`, flushed to disk, with `mode`.

    The caller moves it into place, and removes it when that fails.
    """
    # path-name: only names the temporary file beside the target.
    descriptor, name = tempfile.mkstemp(dir=target.parent, prefix=f".{target.name}.", suffix=".tmp")
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.chmod(mode)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return temporary
