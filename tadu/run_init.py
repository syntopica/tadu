"""The init command."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from tadu.create_missing_file import create_missing_file
from tadu.fresh_log_text import fresh_log_text
from tadu.fresh_todo_text import fresh_todo_text
from tadu.is_blocked_target import is_blocked_target
from tadu.run_sync import run_sync

if TYPE_CHECKING:
    from datetime import date


def run_init(path: str, file: str | None, *, write: bool, today: date) -> int:
    """Add the rule block, then create the backlog files that are missing."""
    root = Path(path)
    if not root.is_dir():
        print(f"{root}: not a directory", file=sys.stderr)
        return 2
    targets = ((root / "TODO.md", fresh_todo_text()), (root / "TODO_LOG.md", fresh_log_text(today)))
    blocked = [target for target, _ in targets if is_blocked_target(target)]
    if blocked:
        print(f"{blocked[0]}: not a regular file; fix by hand", file=sys.stderr)
        return 2
    status = run_sync(path, file, write=write, adopt_legacy=False)
    if status != 0:
        return status
    for target, text in targets:
        create_missing_file(target, text, write=write)
    return 0
