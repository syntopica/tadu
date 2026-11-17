"""Pick the task a close request names."""

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


def task_to_close(todo: Path, args: argparse.Namespace) -> TaskFile:
    """The task named by --id, else the one open task whose title contains --match."""
    if args.id:
        return locate_task(todo, args.id)
    if not args.match:
        msg = "give --id, or --match with text from the task's title"
        raise TaskCommandError(msg)
    files, _ = load_task_files(todo, (OPEN_DIR,))
    found = [file for file in files if args.match in (task_str(file.task, "title") or "")]
    if len(found) == 1:
        return found[0]
    names = ", ".join(f"{file.path.stem} {task_str(file.task, 'title')!r}" for file in found)
    msg = f"{len(found)} open tasks match {args.match!r}" + (f": {names}" if names else "")
    raise TaskCommandError(msg)
