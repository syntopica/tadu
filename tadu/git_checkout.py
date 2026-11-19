"""Where a directory sits in its git repository."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.run_git import run_git

if TYPE_CHECKING:
    from pathlib import Path


def git_checkout(root: Path) -> tuple[str, bool]:
    """Where `root` sits in its repository, and whether the clone is shallow.

       The place is the path from the repository's top, empty or ending in `/`.
    HistoryError when `root`
       is not inside a git repository.
    """
    said = run_git(root, ("rev-parse", "--show-prefix", "--is-shallow-repository")).split("\n")
    return said[0], said[1] == "true"
