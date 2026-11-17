"""Every task file of a backlog with the findings about it alone, cached per file."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.cached_payloads import cached_payloads
from tadu.checked_file import checked_file
from tadu.checked_payload import checked_payload
from tadu.todo_layout import ARCHIVE_DIR, CLOSED_DIR, OPEN_DIR

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.finding import Finding
    from tadu.task_file import TaskFile


def checked_task_files(todo: Path) -> list[tuple[TaskFile | None, tuple[Finding, ...]]]:
    """open/, closed/ and archive/ in path order: (file or None, findings about it alone)."""
    return [
        checked_file(todo / folder / name, payload)
        for folder in (OPEN_DIR, CLOSED_DIR, ARCHIVE_DIR)
        for name, payload in cached_payloads(todo / folder, "checks", todo, checked_payload)
    ]
