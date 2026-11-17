"""Validate a task, then write it where its state says, or only say what would change."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.canonical_task_text import canonical_task_text
from tadu.task_command_error import TaskCommandError
from tadu.task_location import task_location
from tadu.task_problems import task_problems
from tadu.write_file_atomically import write_file_atomically

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.task_file import TaskFile


def save_task(todo: Path, task: dict[str, object], old: TaskFile | None, *, write: bool) -> str:
    """The relative path written (or to be written); TaskCommandError when the task is invalid.

    Empty values count as absent, as the writer leaves them out. Every command writes through
    here, so none can produce a file doctor would reject. A file from a newer format version is
    never rewritten.
    """
    if old is not None and not old.writable:
        msg = f"{old.path.name}: written by a newer tadu format; this tool will not rewrite it"
        raise TaskCommandError(msg)
    cleaned = {key: value for key, value in task.items() if value not in (None, "", [], {})}
    problems = task_problems(cleaned)
    if problems:
        msg = "refused, the task would be invalid: " + "; ".join(problems)
        raise TaskCommandError(msg)
    target = task_location(todo, cleaned)
    if write:
        target.parent.mkdir(parents=True, exist_ok=True)
        write_file_atomically(target, canonical_task_text(cleaned))
        if old is not None and old.path != target:
            old.path.unlink()
    return target.relative_to(todo.parent).as_posix()
