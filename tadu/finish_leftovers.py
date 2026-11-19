"""Finish a migration whose TODO.md or TODO_LOG.md is still beside the task backlog."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.complete_migration import complete_migration
from tadu.unplaced_refusal import unplaced_refusal
from tadu.v1_texts import v1_texts

if TYPE_CHECKING:
    from pathlib import Path


def finish_leftovers(root: Path, *, write: bool) -> int:
    """Bring all the files hold into todo/, then remove them; exit 2 when refused.

    However they came to be there (a migration that stopped, by this tadu or an older one,
    files edited or added since), each item merges into its task or becomes one, and the
    files go only once nothing they hold is missing. Text of TODO.md outside its items is
    refused, as by a first migration: only a person can tell which task it belongs to.
    """
    texts = v1_texts(root)
    refusal = unplaced_refusal(root) if "TODO.md" in texts else None
    if refusal is not None:
        print(f"tadu migrate: {root}: {refusal}", file=sys.stderr)
        return 2
    return complete_migration(root, texts, None, write=write)
