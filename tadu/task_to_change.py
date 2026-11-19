"""Pick the task a change or a close names."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.load_task_files import load_task_files
from tadu.locate_task import locate_task
from tadu.task_command_error import TaskCommandError
from tadu.task_str import task_str
from tadu.todo_layout import OPEN_DIR

if TYPE_CHECKING:
    import argparse
    from pathlib import Path

    from tadu.task_file import TaskFile


def task_to_change(todo: Path, args: argparse.Namespace, *, open_only: bool) -> TaskFile:
    """The task named by --id, else the one open task whose title contains --match.

    With `open_only`, a closed task named by its id is refused. TaskCommandError when no task,
    or more than one, is named.
    """
    match = getattr(args, "match", None)
    if args.id:
        found = locate_task(todo, args.id)
        # path-name: open/ is the directory of a backlog's open tasks; the backlog found it there.
        if open_only and found.path.parent.name != OPEN_DIR:
            msg = f"{found.path.stem} is closed"
            raise TaskCommandError(msg)
        return found
    if not match:
        msg = "give --id, or --match with text from the task's title"
        raise TaskCommandError(msg)
    files, _ = load_task_files(todo, (OPEN_DIR,))
    candidates = [file for file in files if match in (task_str(file.task, "title") or "")]
    if len(candidates) == 1:
        return candidates[0]
    names = ", ".join(f"{file.path.stem} {task_str(file.task, 'title')!r}" for file in candidates)
    msg = f"{len(candidates)} open tasks match {match!r}" + (f": {names}" if names else "")
    raise TaskCommandError(msg)
