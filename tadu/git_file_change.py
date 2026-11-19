"""One file a commit changed."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GitFileChange:
    """The path from the repository's top, its blob in each parent, and its blob after the commit.

    An all-zero blob id means the file is absent on that side.
    """

    path: str
    before: tuple[str, ...]
    after: str
