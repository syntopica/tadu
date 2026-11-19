"""Copy a backlog's files into another directory."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def copy_backlog(files: dict[str, bytes], destination: Path) -> None:
    """Write each file (path inside the backlog, bytes) under `destination`."""
    for path, data in files.items():
        target = destination / path
        # writes: a scratch copy in a temporary folder that is removed, never a backlog.
        target.parent.mkdir(parents=True, exist_ok=True)
        # writes: the same scratch copy.
        target.write_bytes(data)
