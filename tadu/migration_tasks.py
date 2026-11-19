"""Convert a whole tadu v1 backlog into tasks (format v2)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.converted_tasks import converted_tasks
from tadu.v1_texts import v1_texts

if TYPE_CHECKING:
    from pathlib import Path


def migration_tasks(root: Path) -> tuple[tuple[dict[str, object], ...], dict[str, str]]:
    """Every task converted_tasks makes of root's backlog, and category slug -> display name."""
    converted = converted_tasks(v1_texts(root))
    categories: dict[str, str] = {}
    for task, shown, _ in converted:
        if shown is not None:
            categories.setdefault(str(task["category"]), shown)
    return tuple(task for task, _, _ in converted), categories
