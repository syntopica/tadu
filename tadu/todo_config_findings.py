"""Findings about a task backlog's configuration file."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.finding import Finding
from tadu.read_todo_config import read_todo_config
from tadu.task_file_error import TaskFileError
from tadu.todo_config_problems import todo_config_problems
from tadu.todo_layout import TODO_CONFIG
from tadu.unreadable_file_error import UnreadableFileError

if TYPE_CHECKING:
    from pathlib import Path


def todo_config_findings(todo: Path) -> tuple[tuple[Finding, ...], dict[str, object]]:
    """C001 when todo/tadu.json is missing, C002 per problem, E001 when unreadable; and the config.

    The config is empty when it could not be read, so the task checks still run.
    """
    path = str(todo / TODO_CONFIG)
    try:
        config = read_todo_config(todo)
    except UnreadableFileError as error:
        return (Finding("E001", "error", path, 0, str(error)),), {}
    except TaskFileError as error:
        code = "C001" if error.reason == "missing" else "C002"
        return (Finding(code, "error", path, 0, error.reason),), {}
    problems = todo_config_problems(config)
    return tuple(Finding("C002", "error", path, 0, problem) for problem in problems), config
