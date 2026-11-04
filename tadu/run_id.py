"""The id command."""

from __future__ import annotations

import sys
from pathlib import Path

from tadu.backlog_lock import backlog_lock
from tadu.plan_ids import plan_ids
from tadu.print_diff import print_diff
from tadu.run_doctor import run_doctor
from tadu.write_backlog_file import write_backlog_file


def run_id(path: str, key: str | None, *, write: bool) -> int:
    """Give open items without an ID a fresh one; print the diff, apply with write."""
    root = Path(path)
    if not root.is_dir():
        print(f"{root}: not a directory", file=sys.stderr)
        return 2
    with backlog_lock(root):
        plan = plan_ids(root, key)
        if plan is None:
            return 2
        target, before, after = plan
        print_diff(str(target), before, after)
        if not write or before == after:
            return 0
        written = write_backlog_file(target, before, after)
    return run_doctor((path,), as_json=False) if written else 2
