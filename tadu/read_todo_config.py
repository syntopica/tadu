"""Read a task backlog's configuration file."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from tadu.read_text_exact import read_text_exact
from tadu.task_file_error import TaskFileError
from tadu.todo_layout import TODO_CONFIG

if TYPE_CHECKING:
    from pathlib import Path


def read_todo_config(todo: Path) -> dict[str, object]:
    """The parsed todo/tadu.json; TaskFileError when it is missing, not JSON or not an object."""
    path = todo / TODO_CONFIG
    if not path.is_file():
        raise TaskFileError(path, "missing")
    try:
        config: object = json.loads(read_text_exact(path))
    except ValueError as error:
        raise TaskFileError(path, f"not JSON ({error})") from error
    if not isinstance(config, dict):
        raise TaskFileError(path, "not a JSON object")
    return config
