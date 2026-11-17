"""The set command."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.apply_task_change import apply_task_change
from tadu.locate_task import locate_task
from tadu.save_task import save_task
from tadu.task_backlog_dir import task_backlog_dir
from tadu.task_command_error import TaskCommandError

if TYPE_CHECKING:
    import argparse
    from datetime import date


def run_set(args: argparse.Namespace, today: date) -> int:
    """Change fields of one task, validated before writing; exit 2 when refused.

    Moving a task to in_progress records `started` the first time, and never moves it back.
    """
    try:
        todo = task_backlog_dir(args.root)
        old = locate_task(todo, args.id)
        task = dict(old.task)
        for change in args.changes:
            task = apply_task_change(task, change, todo)
        if task.get("state") == "in_progress" and "started" not in task:
            task["started"] = today.isoformat()
        changed = sorted(key for key in {*task, *old.task} if task.get(key) != old.task.get(key))
        where = save_task(todo, task, old, write=args.write)
    except TaskCommandError as error:
        print(f"tadu set: {error}", file=sys.stderr)
        return 2
    verb = "wrote" if args.write else "would write"
    note = "" if args.write else " (dry run: add --write)"
    print(f"tadu set: {verb} {where}: {', '.join(changed) or 'no change'}{note}")
    return 0
