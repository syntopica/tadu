"""Convert a whole tadu v1 backlog into tasks (format v2)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.migration_entries import migration_entries
from tadu.migration_files import migration_files
from tadu.read_text_exact import read_text_exact

if TYPE_CHECKING:
    from pathlib import Path


def migration_tasks(root: Path) -> tuple[tuple[dict[str, object], ...], dict[str, str]]:
    """Every item of the backlog's files (see migration_files) as a task, and slug -> category."""
    files = ((name, read_text_exact(path).splitlines()) for path, name in migration_files(root))
    entries = migration_entries(files)
    categories: dict[str, str] = {}
    for task, shown, _, _ in entries:
        categories.setdefault(str(task["category"]), shown)
    return tuple(task for task, _, _, _ in entries), categories
