"""The close command."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from tadu.backlog_lock import backlog_lock
from tadu.prepare_close import prepare_close
from tadu.print_diff import print_diff
from tadu.run_doctor import run_doctor
from tadu.write_closed_backlog import write_closed_backlog

if TYPE_CHECKING:
    from tadu.closing import Closing


def run_close(path: str, match: str, closing: Closing, *, write: bool) -> int:
    """Move the one open item matching `match` to the log; print the diff, apply with write."""
    root = Path(path)
    if not root.is_dir():
        print(f"{root}: not a directory", file=sys.stderr)
        return 2
    with backlog_lock(root):
        plan = prepare_close(root, match, closing)
        if plan is None:
            return 2
        for target, before, after in (plan.log, plan.todo):
            print_diff(str(target), before, after)
        if not write:
            return 0
        written = write_closed_backlog(plan.todo, plan.log, plan.line)
    return run_doctor((path,), as_json=False) if written else 2
