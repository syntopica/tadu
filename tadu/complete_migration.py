"""Bring everything a format 1 backlog holds into the task backlog beside it."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.apply_completion import apply_completion
from tadu.leftover_patterns import REPOSITORY_TEMPORARY
from tadu.plan_completion import plan_completion
from tadu.print_completion import print_completion
from tadu.remove_stale_temporaries import remove_stale_temporaries
from tadu.task_file_error import TaskFileError
from tadu.todo_layout import CLOSED_DIR, OPEN_DIR, TODO_CONFIG, TODO_DIR
from tadu.unreadable_file_error import UnreadableFileError

if TYPE_CHECKING:
    from pathlib import Path


def complete_migration(
    root: Path, texts: dict[str, str], revision: str | None, *, write: bool
) -> int:
    """Print what changes, apply it with `write`; exit 2 when something is refused.

    `texts` come from `revision`, a commit before the migration, or when it is None from the
    files still in the repository, which go once the task backlog holds everything they hold.
    """
    remove = revision is None
    source = revision or " and ".join(texts)
    todo = root / TODO_DIR
    try:
        plan = plan_completion(todo, texts, everything=remove)
    except (TaskFileError, UnreadableFileError) as error:
        print(
            f"tadu migrate: {todo / TODO_CONFIG}: not valid ({error}); fix it first",
            file=sys.stderr,
        )
        return 2
    print_completion(plan, root, source)
    removed = tuple(root / name for name in texts) if remove and not plan.refused else ()
    verb = "" if write else "would "
    changes = len(plan.created) + len(plan.renamed) + len(plan.rewritten) + bool(plan.config)
    print(
        f"tadu migrate: {verb}make {changes} change(s) from {source}"
        + (f"; {verb}remove {' and '.join(texts)}" if removed else "")
        + ("" if write else " (dry run: add --write)")
    )
    if write and not apply_completion(plan, removed):
        return 2
    if write:  # a write killed in an earlier run leaves its temporary file, with nothing to redo
        for folder in (todo, todo / OPEN_DIR, todo / CLOSED_DIR):
            remove_stale_temporaries(folder, REPOSITORY_TEMPORARY)
    return 2 if plan.refused else 0
