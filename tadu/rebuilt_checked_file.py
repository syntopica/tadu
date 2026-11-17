"""Turn a doctor cache payload back into a task file and its findings."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from tadu.finding import Finding
from tadu.task_file import TaskFile

if TYPE_CHECKING:
    from pathlib import Path

Shape = tuple[
    str | None, dict[str, object] | None, bool, list[tuple[str, str, int, str]], str | None
]


def rebuilt_checked_file(
    path: Path, payload: list[object]
) -> tuple[TaskFile | None, tuple[Finding, ...]]:
    """The file and findings of a payload; TypeError or ValueError when it is malformed."""
    text, task, writable, findings, reason = cast("Shape", tuple(payload))
    if reason is not None:
        return None, (Finding("J001", "error", str(path), 0, reason),)
    if not isinstance(text, str) or not isinstance(task, dict):
        raise TypeError(payload)
    own = tuple(Finding(code, level, str(path), line, note) for code, level, line, note in findings)
    return TaskFile(path, text, task, writable), own
