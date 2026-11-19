"""Close a task of a task backlog (format v2)."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.backlog_unchanged import backlog_unchanged
from tadu.closed_copy import closed_copy
from tadu.closed_task import closed_task
from tadu.finished_task import finished_task
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

    Waiting tasks are only reported, never changed. A task a stopped close left in both open/
    and closed/ is finished instead (see finished_task). Exit 2 when the request is refused.
    """
    try:
        todo = task_backlog_dir(args.path)
        old = task_to_close(todo, args)
        recorded = closed_copy(todo, old)
        if recorded is None:
            task = closed_task(old.task, args, day, todo)
        else:
            task = finished_task((old, recorded), args, day, todo)
        report = waiting_report(todo, task)
        if args.write and recorded and not backlog_unchanged((recorded.path, recorded.text)):
            return 2
        where = save_task(todo, task, old, write=args.write)
    except TaskCommandError as error:
        print(f"tadu close: {error}", file=sys.stderr)
        return 2
    verb = "closed" if args.write else "would close"
    if recorded is not None:
        verb = f"{'finished' if args.write else 'would finish'} the stopped close of"
    print(f"tadu close: {verb} {old.path.stem} as {task['state']} -> {where}")
    for line in report:
        print(line)
    if not args.write:
        print("(dry run: add --write)")
    return 0
