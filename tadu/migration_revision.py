"""Find the commits that may still hold the Markdown backlog a migration removed."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.git_output import git_output
from tadu.todo_layout import TODO_CONFIG, TODO_DIR
from tadu.v1_texts import V1_FILES

if TYPE_CHECKING:
    from pathlib import Path


def migration_revision(root: Path) -> tuple[str, ...]:
    """The revisions to read it from, the likeliest first.

    The commit before the one that first added todo/tadu.json (the migration itself), then
    the one before the latest commit that deleted TODO.md or TODO_LOG.md: a TODO.md written
    by hand and removed later is deleted after the migration, and must not hide it.
    """
    config = f"{TODO_DIR}/{TODO_CONFIG}"
    added = (git_output(root, "log", "--format=%H", "--diff-filter=A", "--", config) or b"").split()
    deleted = git_output(root, "log", "-n", "1", "--format=%H", "--diff-filter=D", "--", *V1_FILES)
    found = [*added[-1:], *(deleted or b"").split()]
    # keys: one revision per commit, in order; a commit found twice is meant to collapse
    return tuple(dict.fromkeys(f"{commit.decode()}^" for commit in found))
