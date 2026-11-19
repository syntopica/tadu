"""The migrate --recover command."""

from __future__ import annotations

import sys
from pathlib import Path

from tadu.complete_migration import complete_migration
from tadu.is_task_backlog import is_task_backlog
from tadu.record_recovery import record_recovery
from tadu.recovery_source import recovery_source
from tadu.start_recovery import start_recovery
from tadu.todo_layout import TODO_DIR


def run_recover(path: str, revision: str | None, *, write: bool) -> int:
    """Bring into the task backlog what an older migrate lost, read from git; exit 2 if refused.

    The Markdown backlog comes from recovery_source. IDs come back, fields left as note lines
    become keys, and the text that migrate dropped is added (complete_migration); tasks
    edited or deleted since stay as they are. A recovery is done once per commit
    (start_recovery): tadu.json marks it pending before it writes, and recovered once it
    finished, after which running it again changes nothing, so what it brought and was
    removed since does not come back.
    """
    root = Path(path)
    if not is_task_backlog(root):
        print(f"tadu migrate: {root}: not a task backlog; nothing to recover", file=sys.stderr)
        return 2
    source = recovery_source(root, revision)
    if isinstance(source, str):
        print(f"tadu migrate: {root}: {source}", file=sys.stderr)
        return 2
    commit, texts = source
    todo = root / TODO_DIR
    held = start_recovery(todo, commit, write=write)
    if held is not None:
        print(f"tadu migrate: {held[1]}", file=sys.stderr if held[0] else sys.stdout)
        return held[0]
    status = complete_migration(root, texts, commit[:12], write=write)
    recorded = not (write and status == 0) or record_recovery(todo, commit)
    return status if recorded else 2
