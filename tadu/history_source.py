"""Where the history of one Markdown backlog is read from."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.blob_reader import BlobReader


@dataclass(frozen=True)
class HistorySource:
    """A checkout and how to read the versions of its backlog files.

    `root` sits at `prefix` in its repository; `paths` are the backlog's files relative to it;
    items are keyed with the `repository` label; `blobs` reads the versions.
    """

    root: Path
    prefix: str
    paths: tuple[str, ...]
    repository: str
    blobs: BlobReader

    @staticmethod
    def pathspec(path: str) -> str:
        """A file of the checkout as a git pathspec, taken literally."""
        return f":(literal){path}"

    def name(self, commit: str, path: str) -> str:
        """The git name of a file of the checkout in a commit."""
        return f"{commit}:{self.prefix}{path}"
