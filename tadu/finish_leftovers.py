"""Finish a migration whose TODO.md or TODO_LOG.md is still beside the task backlog."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.complete_migration import complete_migration
from tadu.v1_texts import v1_texts

if TYPE_CHECKING:
    from pathlib import Path


def finish_leftovers(root: Path, *, write: bool) -> int:
    """Bring all the files hold into todo/, then remove them.

    However they came to be there (a migration that stopped, by this tadu or an older one,
    files edited or added since), each item merges into its task or becomes one, and the
    files go only once nothing they hold is missing. Text outside the items becomes tasks, as
    by a first migration.
    """
    texts = v1_texts(root)
    return complete_migration(root, texts, None, write=write)
