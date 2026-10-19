"""Find the repository root that holds a backlog, walking up from a directory."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def nearest_backlog_root(start: Path) -> Path | None:
    """The first of `start` and its ancestors that contains a TODO.md, or None."""
    for directory in (start, *start.parents):
        if (directory / "TODO.md").is_file():
            return directory
    return None
