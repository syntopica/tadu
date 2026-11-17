"""Find the task directory of a repository a command was pointed at."""

from __future__ import annotations

from pathlib import Path

from tadu.is_task_backlog import is_task_backlog
from tadu.task_command_error import TaskCommandError
from tadu.todo_layout import TODO_DIR


def task_backlog_dir(root: str) -> Path:
    """root/todo when root holds a task backlog; TaskCommandError otherwise."""
    path = Path(root)
    if not is_task_backlog(path):
        msg = f"{root}: no todo/tadu.json; run tadu migrate, or tadu init --format 2"
        raise TaskCommandError(msg)
    return path / TODO_DIR
