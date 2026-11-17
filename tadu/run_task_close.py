"""Close a task of a task backlog (format v2)."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.closed_task import closed_task
from tadu.save_task import save_task
from tadu.task_backlog_dir import task_backlog_dir
from tadu.task_command_error import TaskCommandError
from tadu.task_to_close import task_to_close
from tadu.waiting_report import waiting_report

if TYPE_CHECKING:
    import argparse
    from datetime import date


def run_task_close(args: argparse.Namespace, day: date) -> int:
    """Append the closing keys, move the file to closed/, and report the tasks waiting on it.

    Waiting tasks are only reported, never changed. Exit 2 when the request is refused.
    """
    try:
        todo = task_backlog_dir(args.path)
        old = task_to_close(todo, args)
        task = closed_task(old.task, args, day, todo)
        report = waiting_report(todo, task)
        where = save_task(todo, task, old, write=args.write)
    except TaskCommandError as error:
        print(f"tadu close: {error}", file=sys.stderr)
        return 2
    verb = "closed" if args.write else "would close"
    print(f"tadu close: {verb} {old.path.stem} as {task['state']} -> {where}")
    for line in report:
        print(line)
    if not args.write:
        print("(dry run: add --write)")
    return 0
