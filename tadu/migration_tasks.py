"""Convert a whole tadu v1 backlog into tasks (format v2)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.read_text_exact import read_text_exact
from tadu.stable_task_id import stable_task_id
from tadu.v1_item_blocks import v1_item_blocks
from tadu.v1_task import v1_task

if TYPE_CHECKING:
    from pathlib import Path

V1_FILES = ("TODO.md", "TODO_LOG.md")


def migration_tasks(root: Path) -> tuple[tuple[dict[str, object], ...], dict[str, str]]:
    """Every item of TODO.md then TODO_LOG.md as a task, and category slug -> display name.

    An id used twice (doctor's F002 in v1) keeps its first task; the others get a new stable id.
    """
    tasks: list[dict[str, object]] = []
    categories: dict[str, str] = {}
    seen: set[object] = set()
    for name in V1_FILES:
        path = root / name
        lines = read_text_exact(path).splitlines() if path.is_file() else []
        for number, (block, section) in enumerate(v1_item_blocks(lines)):
            task, shown = v1_task(block, section, f"{name}:{number}")
            if task["id"] in seen:
                task["id"] = stable_task_id(f"{name}:{number}", str(task["title"]), "repeated id")
            seen.add(task["id"])
            categories.setdefault(str(task["category"]), shown)
            tasks.append(task)
    return tuple(tasks), categories
