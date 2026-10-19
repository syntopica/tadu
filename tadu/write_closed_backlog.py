"""Write a closed item's two files, log first."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.backlog_unchanged import backlog_unchanged
from tadu.write_file_atomically import write_file_atomically

if TYPE_CHECKING:
    from pathlib import Path


def write_closed_backlog(
    todo: tuple[Path, str, str], log: tuple[Path, str, str], line: int
) -> bool:
    """Write each (path, read text, new text) if unchanged since read; False after reporting."""
    if not backlog_unchanged((todo[0], todo[1]), (log[0], log[1])):
        return False
    try:
        write_file_atomically(log[0], log[2])
    except OSError as error:
        print(f"{log[0]}: not written ({error}); nothing changed", file=sys.stderr)
        return False
    try:
        write_file_atomically(todo[0], todo[2])
    except OSError as error:
        message = f"logged but not removed ({error}); delete the item at line {line} by hand"
        print(f"{todo[0]}: {message}", file=sys.stderr)
        return False
    return True
