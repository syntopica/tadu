"""One file a proposal changes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FileChange:
    """The path inside the backlog directory, and the bytes before and after.

    `before` is None for a file the change adds and `after` None for one it deletes.
    """

    path: str
    before: bytes | None
    after: bytes | None
