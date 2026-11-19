"""Plan the moves an archive policy calls for."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.load_task_files import load_task_files
from tadu.planned_archive_moves import planned_archive_moves
from tadu.todo_layout import ARCHIVE_DIR, CLOSED_DIR

if TYPE_CHECKING:
    from datetime import date
    from pathlib import Path


def archive_moves(
    todo: Path, policy: dict[str, object], today: date
) -> tuple[tuple[Path, Path], ...]:
    """The moves planned_archive_moves plans, for the task files of closed/ and archive/."""
    closed, _ = load_task_files(todo, (CLOSED_DIR,))
    archived, _ = load_task_files(todo, (ARCHIVE_DIR,))
    return planned_archive_moves((closed, archived), todo, policy, today)
