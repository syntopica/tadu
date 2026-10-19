"""Read a repository's backlog and log for a change to both."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.read_text_exact import read_text_exact

if TYPE_CHECKING:
    from pathlib import Path


def read_backlog(root: Path) -> tuple[str, str] | None:
    """The texts of TODO.md and TODO_LOG.md; None after reporting the first one missing."""
    todo, log = root / "TODO.md", root / "TODO_LOG.md"
    for target in (todo, log):
        if not target.is_file():
            print(f"{target}: missing; start the backlog with `tadu init`", file=sys.stderr)
            return None
    return read_text_exact(todo), read_text_exact(log)
