"""Record in todo/tadu.json that a recovery from a commit is done."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from tadu.backlog_unchanged import backlog_unchanged
from tadu.pending_recovery import PENDING_KEY
from tadu.read_text_exact import read_text_exact
from tadu.read_todo_config import read_todo_config
from tadu.recovered_commits import RECOVERED_KEY, recovered_commits
from tadu.todo_layout import TODO_CONFIG
from tadu.write_file_atomically import write_file_atomically

if TYPE_CHECKING:
    from pathlib import Path


def record_recovery(todo: Path, commit: str) -> bool:
    """Record `commit` as recovered, no longer pending; False after reporting when tadu.json changed.

    Written last, once everything the recovery brings is: a run that stops before it is
    finished by running it again, and one that got here is never redone, so what it brought
    and was removed since does not come back.
    """
    path = todo / TODO_CONFIG
    before = read_text_exact(path)
    config = read_todo_config(todo)
    after = {key: value for key, value in config.items() if key != PENDING_KEY}
    after[RECOVERED_KEY] = [*recovered_commits(todo), commit]
    if not backlog_unchanged((path, before)):
        return False
    write_file_atomically(path, json.dumps(after, indent=2, ensure_ascii=False) + "\n")
    return True
