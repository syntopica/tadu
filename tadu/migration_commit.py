"""Tell the commit that migrated a backlog to task files."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from tadu.todo_layout import TODO_CONFIG, TODO_DIR

if TYPE_CHECKING:
    from tadu.git_commit import GitCommit


def migration_commit(commit: GitCommit, prefix: str, backlog: str) -> bool:
    """Whether the commit removed the backlog's TODO.md and added todo/tadu.json, as migrate does.

    `prefix` is the checkout's place in the repository, `backlog` the backlog's folder in it.
    """
    folder = PurePosixPath(prefix or ".", backlog)
    todo_md = (folder / "TODO.md").as_posix()
    config = (folder / TODO_DIR / TODO_CONFIG).as_posix()
    removed = any(c.path == todo_md and not c.after.strip("0") for c in commit.files)
    added = any(c.path == config and not any(b.strip("0") for b in c.before) for c in commit.files)
    return removed and added
