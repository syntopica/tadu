"""Route `tadu add` to the command of the repository's backlog format."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from tadu.add_command import add_command
from tadu.is_task_backlog import is_task_backlog
from tadu.run_task_add import run_task_add
from tadu.with_backlog_lock import with_backlog_lock

if TYPE_CHECKING:
    import argparse
    from datetime import date


def dispatch_add(args: argparse.Namespace, today: date) -> int:
    """A task backlog (todo/tadu.json) gets a task file; any other repository gets a TODO.md item."""
    if is_task_backlog(Path(args.path)):
        return with_backlog_lock(args.path, lambda: run_task_add(args, today))
    return add_command(args)
