"""Detect a backlog path that holds something other than a readable file."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def is_blocked_target(path: Path) -> bool:
    """True for a directory, a dangling symlink or any other non-file at `path`."""
    if path.is_symlink() and not path.exists():
        return True
    return path.exists() and not path.is_file()
