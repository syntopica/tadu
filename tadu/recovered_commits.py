"""The commits a task backlog was already recovered from."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.read_todo_config import read_todo_config
from tadu.task_file_error import TaskFileError

if TYPE_CHECKING:
    from pathlib import Path

RECOVERED_KEY = "x-format-1-recovered"


def recovered_commits(todo: Path) -> tuple[str, ...]:
    """The commit ids `tadu migrate --recover` finished from, as todo/tadu.json records them."""
    try:
        kept = read_todo_config(todo).get(RECOVERED_KEY)
    except TaskFileError:
        return ()
    return (
        tuple(commit for commit in kept if isinstance(commit, str))
        if isinstance(kept, list)
        else ()
    )
