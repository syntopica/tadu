"""Convert the files of a tadu v1 backlog into tasks, keeping where each came from."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.stable_task_id import stable_task_id
from tadu.v1_item_blocks import v1_item_blocks
from tadu.v1_task import v1_task

if TYPE_CHECKING:
    from collections.abc import Iterable


def migration_entries(
    files: Iterable[tuple[str, list[str]]],
) -> list[tuple[dict[str, object], str, str, int]]:
    """(task, category display name, file name, item number in the file) for every item.

    Files come as (name relative to the backlog, lines), in migration_files order; the name
    and number make the id of an item without one. An id used twice (doctor's F002 in v1)
    keeps its first task; the others get a new stable id.
    """
    entries: list[tuple[dict[str, object], str, str, int]] = []
    seen: set[object] = set()
    for name, lines in files:
        for number, (block, section) in enumerate(v1_item_blocks(lines)):
            task, shown = v1_task(block, section, f"{name}:{number}")
            if task["id"] in seen:
                task["id"] = stable_task_id(f"{name}:{number}", str(task["title"]), "repeated id")
            seen.add(task["id"])
            entries.append((task, shown, name, number))
    return entries
