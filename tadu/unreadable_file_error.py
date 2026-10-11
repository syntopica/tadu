"""The error raised when a checked file cannot be read."""

from __future__ import annotations

from pathlib import Path


class UnreadableFileError(Exception):
    """A file that could not be read as UTF-8 text, with the reason."""

    def __init__(self, path: Path, reason: str) -> None:
        super().__init__(f"{path} could not be read: {reason}")
        self.path = path
        self.reason = reason
