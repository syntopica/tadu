"""The init command for a task backlog (format 2)."""

from __future__ import annotations

import sys
from pathlib import Path

from tadu.create_missing_file import create_missing_file
from tadu.fresh_todo_config_text import fresh_todo_config_text
from tadu.is_blocked_target import is_blocked_target
from tadu.run_sync import run_sync
from tadu.todo_layout import TODO_CONFIG, TODO_DIR


def run_task_init(path: str, file: str | None, *, write: bool) -> int:
    """Add the rule block, then create todo/tadu.json when it is missing.

    A repository that already has a TODO.md is pointed to tadu migrate instead.
    """
    root = Path(path)
    target = root / TODO_DIR / TODO_CONFIG
    if (root / "TODO.md").is_file():
        print(f"{root / 'TODO.md'}: exists; run tadu migrate to convert it", file=sys.stderr)
        return 2
    folder = target.parent
    if ((folder.exists() or folder.is_symlink()) and not folder.is_dir()) or is_blocked_target(
        target
    ):
        print(f"{target}: not a regular file; fix by hand", file=sys.stderr)
        return 2
    status = run_sync(path, file, write=write, adopt_legacy=False)
    if status != 0:
        return status
    if write:
        target.parent.mkdir(exist_ok=True)
    create_missing_file(target, fresh_todo_config_text(), write=write)
    return 0
