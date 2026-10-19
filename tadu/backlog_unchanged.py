"""Check that the backlog files still hold what was read."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.read_text_exact import read_text_exact
from tadu.unreadable_file_error import UnreadableFileError

if TYPE_CHECKING:
    from pathlib import Path


def backlog_unchanged(*files: tuple[Path, str]) -> bool:
    """True when each (path, text read) still matches; False after reporting."""
    try:
        changed = any(read_text_exact(path) != before for path, before in files)
    except UnreadableFileError as error:
        print(f"{error.path}: {error}; nothing written", file=sys.stderr)
        return False
    if changed:
        print(f"{files[0][0].parent}: backlog changed while closing; run again", file=sys.stderr)
    return not changed
