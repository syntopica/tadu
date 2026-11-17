"""One task file as read from disk."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True)
class TaskFile:
    """The file's path and text, its task object, and whether this tool may rewrite it.

    A file written by a newer format version is readable as far as its keys are known, but
    never writable: rewriting it would drop the keys this tool does not know.
    """

    path: Path
    text: str
    task: dict[str, object]
    writable: bool
