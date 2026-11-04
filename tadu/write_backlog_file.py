"""Write one backlog file that nothing else changed since it was read."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.backlog_unchanged import backlog_unchanged
from tadu.write_file_atomically import write_file_atomically

if TYPE_CHECKING:
    from pathlib import Path


def write_backlog_file(target: Path, before: str, after: str) -> bool:
    """Replace `before` with `after` atomically; False after reporting a change or a failure."""
    if not backlog_unchanged((target, before)):
        return False
    try:
        write_file_atomically(target, after)
    except OSError as error:
        print(f"{target}: not written ({error}); nothing changed", file=sys.stderr)
        return False
    return True
