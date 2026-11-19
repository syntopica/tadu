"""Which format a repository's backlog is in."""

from __future__ import annotations

from pathlib import Path

from tadu.is_task_backlog import is_task_backlog
from tadu.task_format_version import TASK_FORMAT_VERSION


def backlog_format(root: str) -> int:
    """2 for a task backlog (todo/tadu.json), else 1: TODO.md and TODO_LOG.md."""
    return TASK_FORMAT_VERSION if is_task_backlog(Path(root)) else 1
