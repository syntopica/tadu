"""The add command of a task backlog (format v2)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from tadu.new_task import new_task
from tadu.save_task import save_task
from tadu.similar_task_lines import similar_task_lines
from tadu.task_add_refusal import task_add_refusal
from tadu.task_backlog_dir import task_backlog_dir
from tadu.task_command_error import TaskCommandError

if TYPE_CHECKING:
    import argparse
    from datetime import date


def run_task_add(args: argparse.Namespace, today: date) -> int:
    """Show similar tasks, then write the new one (or say where it would go); exit 2 when refused."""
    refusal = task_add_refusal(args)
    if refusal is not None:
        print(f"tadu add: {refusal}", file=sys.stderr)
        return 2
    try:
        todo = task_backlog_dir(args.path)
        task = new_task(args, today, todo)
        for line in similar_task_lines(Path(args.path), args.title):
            print(line)
        where = save_task(todo, task, None, write=args.write)
    except TaskCommandError as error:
        print(f"tadu add: {error}", file=sys.stderr)
        return 2
    print(
        f"tadu add: {'wrote' if args.write else 'would write'} {where}"
        + ("" if args.write else " (dry run: add --write)")
    )
    return 0
