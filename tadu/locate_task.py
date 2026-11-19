"""Find a task file by its id or a unique prefix of it."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.read_task_file import read_task_file
from tadu.short_keys import MIN_LENGTH
from tadu.task_command_error import TaskCommandError
from tadu.todo_layout import ARCHIVE_DIR, CLOSED_DIR, OPEN_DIR, TASK_SUFFIX

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.task_file import TaskFile


def locate_task(todo: Path, key: str, *, open_when_split: bool = False) -> TaskFile:
    """The task whose id is `key`, or starts with it (10 characters or more); never a guess.

    Files are found by name, so the archive is not parsed. TaskCommandError when no task or
    more than one matches. A task in both open/ and closed/, as a close that stopped halfway
    leaves it, gives its open file with `open_when_split` (to finish the close), else an error
    saying so.
    """
    if not key.startswith("t-") or len(key) < MIN_LENGTH:
        msg = f"{key}: give a task id, or at least its first {MIN_LENGTH} characters"
        raise TaskCommandError(msg)
    found = sorted(
        path
        for folder in (OPEN_DIR, CLOSED_DIR, ARCHIVE_DIR)
        for path in (todo / folder).rglob(f"{key}*{TASK_SUFFIX}")
    )
    # path-name: the file stem is the task id, unique within one backlog
    exact = [path for path in found if path.stem == key]
    if len(exact) == 1 or len(found) == 1:
        return read_task_file((exact or found)[0])
    if not found:
        msg = f"{key}: no such task"
        raise TaskCommandError(msg)
    # path-name: the file stem is the task id, unique within one backlog
    ids = sorted({path.stem for path in found})
    split = {todo / folder / f"{ids[0]}{TASK_SUFFIX}" for folder in (OPEN_DIR, CLOSED_DIR)}
    if len(ids) == 1 and set(found) == split:
        if open_when_split:
            return read_task_file(todo / OPEN_DIR / f"{ids[0]}{TASK_SUFFIX}")
        msg = (
            f"{ids[0]}: in open/ and closed/, as a close that stopped halfway leaves it; "
            f"run tadu close --id {ids[0]} again to finish it"
        )
        raise TaskCommandError(msg)
    msg = f"{key}: ambiguous: {', '.join(ids)}"
    raise TaskCommandError(msg)
