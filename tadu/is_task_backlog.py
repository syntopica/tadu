"""Tell a task backlog (format v2) from a Markdown one."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.refuse_newer_format import refuse_newer_format
from tadu.todo_layout import TODO_CONFIG, TODO_DIR

if TYPE_CHECKING:
    from pathlib import Path


def is_task_backlog(directory: Path) -> bool:
    """True when the directory holds todo/tadu.json; NewerFormatError if a newer tadu wrote it."""
    config = directory / TODO_DIR / TODO_CONFIG
    if not config.is_file():
        return False
    refuse_newer_format(config)
    return True
