"""The claim command."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.claimed_task import claimed_task
from tadu.locate_task import locate_task
from tadu.save_task import save_task
from tadu.task_backlog_dir import task_backlog_dir
from tadu.task_command_error import TaskCommandError

if TYPE_CHECKING:
    import argparse
    from datetime import date


def run_claim(args: argparse.Namespace, today: date) -> int:
    """Take a task: the assignee, in_progress and started in one change; exit 2 when refused.

    Two agents claiming the same task on two branches change the same lines, so git reports a
    conflict instead of merging a double claim.
    """
    try:
        todo = task_backlog_dir(args.path)
        old = locate_task(todo, args.id)
        task = claimed_task(todo, old, args, today)
        where = save_task(todo, task, old, write=args.write)
    except TaskCommandError as error:
        print(f"tadu claim: {error}", file=sys.stderr)
        return 2
    verb = "claimed" if args.write else "would claim"
    print(
        f"tadu claim: {verb} {where} for {args.who}"
        + ("" if args.write else " (dry run: add --write)")
    )
    return 0
