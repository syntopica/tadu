"""One backlog `tadu changes` reads, and how to read it."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.blob_reader import BlobReader


@dataclass(frozen=True)
class ChangeSource:
    """A backlog's repository label and project, as its items carry them, and where it is.

    `root` is the checkout, at `prefix` in its repository; `backlog` the backlog's folder in
    it; `blobs` the reader of file versions.
    """

    repository: str
    project: str | None
    root: Path
    prefix: str
    backlog: str
    blobs: BlobReader
