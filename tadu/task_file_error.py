"""The error raised when a task file cannot be read as a task."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class TaskFileError(Exception):
    """A task file that is not JSON, not an object, or has no usable format version."""

    def __init__(self, path: Path, reason: str) -> None:
        super().__init__(f"{path}: {reason}")
        self.path = path
        self.reason = reason
