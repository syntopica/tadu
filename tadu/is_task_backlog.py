"""Tell a task backlog (format v2) from a Markdown one."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.todo_layout import TODO_CONFIG, TODO_DIR

if TYPE_CHECKING:
    from pathlib import Path


def is_task_backlog(directory: Path) -> bool:
    """True when the directory holds todo/tadu.json."""
    return (directory / TODO_DIR / TODO_CONFIG).is_file()
