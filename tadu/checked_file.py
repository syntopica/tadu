"""One task file and the findings about it alone, from a doctor cache payload."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.checked_payload import checked_payload
from tadu.rebuilt_checked_file import rebuilt_checked_file

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.finding import Finding
    from tadu.task_file import TaskFile


def checked_file(path: Path, payload: list[object]) -> tuple[TaskFile | None, tuple[Finding, ...]]:
    """The file (None when unreadable, with J001) and its own findings.

    A malformed cached payload (another tool version) is recomputed from the file.
    """
    try:
        return rebuilt_checked_file(path, payload)
    except (TypeError, ValueError):
        return rebuilt_checked_file(path, checked_payload(path))
