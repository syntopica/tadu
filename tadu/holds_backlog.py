"""Tell whether a directory is a repository root with a backlog."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.todo_layout import TODO_CONFIG, TODO_DIR

if TYPE_CHECKING:
    from pathlib import Path


def holds_backlog(directory: Path) -> bool:
    """True when the directory holds a TODO.md or a todo/tadu.json, whatever tadu wrote it.

    It does not read the format: a command that reads the backlog refuses a newer one, and
    one that targets another path must not stop on this directory's.
    """
    return (directory / "TODO.md").is_file() or (directory / TODO_DIR / TODO_CONFIG).is_file()
