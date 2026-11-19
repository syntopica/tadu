"""Route `tadu add` to the command of the repository's backlog format."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.add_command import add_command
from tadu.backlog_format import backlog_format
from tadu.format_refusal import format_refusal
from tadu.operations import OPERATIONS
from tadu.run_task_add import run_task_add
from tadu.task_format_version import TASK_FORMAT_VERSION
from tadu.with_backlog_lock import with_backlog_lock

if TYPE_CHECKING:
    import argparse
    from datetime import date


def dispatch_add(args: argparse.Namespace, today: date) -> int:
    """A task backlog (todo/tadu.json) gets a task file; any other repository gets a TODO.md item.

    An option only the other format takes exits 2 (see format_refusal). A task file is
    written under the backlog's lock.
    """
    format_ = backlog_format(args.path)
    refusal = format_refusal(OPERATIONS["add"], args, format_)
    if refusal is not None:
        print(f"tadu add: {refusal}", file=sys.stderr)
        return 2
    if format_ == TASK_FORMAT_VERSION:
        return with_backlog_lock(args.path, lambda: run_task_add(args, today))
    return add_command(args)
