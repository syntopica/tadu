"""The mark command: set an open item's state and fields, with a note saying why."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from tadu.backlog_format import backlog_format
from tadu.first_problem import first_problem
from tadu.format_refusal import format_refusal
from tadu.mark_field_values import mark_field_values
from tadu.markdown_mark import markdown_mark
from tadu.operations import OPERATIONS
from tadu.run_task_mark import run_task_mark
from tadu.task_format_version import TASK_FORMAT_VERSION
from tadu.text_problem import text_problem

if TYPE_CHECKING:
    import argparse
    from datetime import date


def mark_command(args: argparse.Namespace, today: date) -> int:
    """Refuse a blank or multi-line value and a block without its blocker, then mark.

    A task backlog takes the mark as task changes; TODO.md as lines.
    """
    fields = mark_field_values(args)
    format_ = backlog_format(args.path)
    values = [args.match or args.id, *([args.note] if args.note is not None else [])]
    values += [value for _, value in fields]
    problem = first_problem(
        [
            text_problem(values),
            "give --state or a field to set" if args.state is None and not fields else None,
            "--state blocked needs a --note naming the blocker"
            if args.state == "blocked" and args.note is None
            else None,
            None if Path(args.path).is_dir() else f"{args.path}: not a directory",
            format_refusal(OPERATIONS["mark"], args, format_),
        ]
    )
    if problem is not None:
        print(f"tadu mark: {problem}", file=sys.stderr)
        return 2
    if format_ == TASK_FORMAT_VERSION:
        return run_task_mark(args, fields, today)
    return markdown_mark(args, fields, today)
