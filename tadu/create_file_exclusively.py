"""Create a file whole, never replacing one that appears meanwhile."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from tadu.leftover_patterns import REPOSITORY_TEMPORARY
from tadu.remove_stale_temporaries import remove_stale_temporaries


def create_file_exclusively(target: Path, text: str) -> None:
    """Write `text` to a sibling temp file, then hard-link it to `target`; FileExistsError if taken.

    Temporary files that earlier writes were killed before linking are removed afterwards.
    """
    # path-name: only names the temporary file beside the target.
    descriptor, name = tempfile.mkstemp(dir=target.parent, prefix=f".{target.name}.", suffix=".tmp")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        Path(name).chmod(0o644)
        Path(target).hardlink_to(name)
    finally:
        Path(name).unlink(missing_ok=True)
    remove_stale_temporaries(target.parent, REPOSITORY_TEMPORARY)
