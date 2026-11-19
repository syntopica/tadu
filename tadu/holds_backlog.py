"""Tell whether a directory is a repository root with a backlog."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.is_task_backlog import is_task_backlog

if TYPE_CHECKING:
    from pathlib import Path


def holds_backlog(directory: Path) -> bool:
    """True when the directory holds a TODO.md or a todo/tadu.json."""
    return (directory / "TODO.md").is_file() or is_task_backlog(directory)
