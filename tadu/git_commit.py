"""One commit of `git log`."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.git_file_change import GitFileChange


@dataclass(frozen=True)
class GitCommit:
    """A commit with its author date (ISO 8601) and the asked-for files it changed.

    A merge lists only files that differ from every parent, as `git log -c` does.
    """

    sha: str
    short: str
    parents: tuple[str, ...]
    date: str
    author: str
    subject: str
    files: tuple[GitFileChange, ...]
