"""Mark in todo/tadu.json that a recovery has started."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from tadu.backlog_unchanged import backlog_unchanged
from tadu.pending_recovery import PENDING_KEY
from tadu.read_text_exact import read_text_exact
from tadu.read_todo_config import read_todo_config
from tadu.task_file_error import TaskFileError
from tadu.todo_layout import TODO_CONFIG
from tadu.unreadable_file_error import UnreadableFileError
from tadu.write_file_atomically import write_file_atomically

if TYPE_CHECKING:
    from pathlib import Path


def mark_recovery(todo: Path, commit: str) -> str | None:
    """Record the recovery from `commit` as pending; why not, when tadu.json cannot take it."""
    path = todo / TODO_CONFIG
    try:
        before = read_text_exact(path)
        config = read_todo_config(todo)
    except (TaskFileError, UnreadableFileError) as error:
        return f"{path}: not valid ({error}); fix it first"
    if not backlog_unchanged((path, before)):
        return f"{path}: changed meanwhile; run again"
    text = json.dumps({**config, PENDING_KEY: commit}, indent=2, ensure_ascii=False) + "\n"
    write_file_atomically(path, text)
    return None
