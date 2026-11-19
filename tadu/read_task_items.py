"""Read the items of a task backlog (format v2)."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from tadu.cached_folder_items import cached_folder_items
from tadu.task_item_order import task_item_order
from tadu.task_states import OPEN_TASK_STATES
from tadu.todo_layout import ARCHIVE_DIR, CLOSED_DIR, OPEN_DIR, TODO_DIR

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.backlog_item import BacklogItem


def read_task_items(root: Path, backlog: str, cutoff: date) -> tuple[BacklogItem, ...]:
    """Open tasks, and closed ones (closed/ and archive/) closed on or after the cutoff.

    A cutoff of date.max asks for open tasks only, and closed/ is not read at all. Archive years
    before the cutoff are not read, and closed tasks outside the window are dropped before they
    become items. Unreadable files are skipped here; doctor reports them. Unchanged files come
    from the item cache (see cached_folder_items).
    """
    todo = root / backlog / TODO_DIR
    archive = todo / ARCHIVE_DIR
    # path-name: year folders inside one archive, unique within it
    years = sorted(p.name for p in archive.iterdir() if p.is_dir()) if archive.is_dir() else []
    recent = [year for year in years if not year.isdecimal() or int(year) >= cutoff.year]
    closed = (
        () if cutoff == date.max else (CLOSED_DIR, *(f"{ARCHIVE_DIR}/{year}" for year in recent))
    )
    since = cutoff.isoformat()

    def keep(state: object, closed: object) -> bool:
        return state in OPEN_TASK_STATES or str(closed or "") >= since

    kept = [
        item
        for folder in (OPEN_DIR, *closed)
        for item in cached_folder_items(todo / folder, root, keep)
    ]
    return tuple(sorted(kept, key=task_item_order))
