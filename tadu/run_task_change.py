"""Change one task of a task backlog: the shared tail of set and mark."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.apply_task_change import apply_task_change
from tadu.empty_values import EMPTY_VALUES
from tadu.save_task import save_task
from tadu.task_backlog_dir import task_backlog_dir
from tadu.task_command_error import TaskCommandError
from tadu.task_to_change import task_to_change

if TYPE_CHECKING:
    import argparse
    from datetime import date


def run_task_change(command: str, args: argparse.Namespace, changes: list[str], today: date) -> int:
    """Apply the `key=value` changes to the task --id (or --match) names; exit 2 when refused.

    Moving a task into in_progress records `started` the first time, and never moves it back;
    changing other fields of a task already in progress leaves `started` as it was.
    """
    try:
        todo = task_backlog_dir(args.path)
        old = task_to_change(todo, args, open_only=command == "mark")
        task = dict(old.task)
        for change in changes:
            task = apply_task_change(task, change, todo)
        moved_in = task.get("state") == "in_progress" and old.task.get("state") != "in_progress"
        if moved_in and "started" not in task:
            task["started"] = today.isoformat()
        changed = sorted(
            key
            for key in {*task, *old.task}
            if task.get(key) != old.task.get(key)
            and not (task.get(key) in EMPTY_VALUES and old.task.get(key) in EMPTY_VALUES)
        )
        where = save_task(todo, task, old, write=args.write)
    except TaskCommandError as error:
        print(f"tadu {command}: {error}", file=sys.stderr)
        return 2
    verb = "wrote" if args.write else "would write"
    note = "" if args.write else " (dry run: add --write)"
    print(f"tadu {command}: {verb} {where}: {', '.join(changed) or 'no change'}{note}")
    return 0
