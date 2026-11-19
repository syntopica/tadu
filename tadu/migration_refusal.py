"""Decide whether a repository can be migrated to a task backlog."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.is_task_backlog import is_task_backlog
from tadu.stopped_close_refusal import stopped_close_refusal
from tadu.todo_layout import TODO_DIR

if TYPE_CHECKING:
    from pathlib import Path


def migration_refusal(root: Path) -> str | None:
    """Why root cannot be migrated, or None.

    It already is a task backlog, todo/ is taken, there is no TODO.md, or a close stopped
    halfway and left an item both open and closed.
    """
    if is_task_backlog(root):
        return "already a task backlog"
    if (root / TODO_DIR).exists():
        return f"{TODO_DIR}/ already exists; move it away first"
    if not (root / "TODO.md").is_file():
        return "no TODO.md"
    return stopped_close_refusal(root)
