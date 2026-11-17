"""Replace a file with a planned text, but only the text that was read."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.backlog_unchanged import backlog_unchanged
from tadu.create_file_exclusively import create_file_exclusively
from tadu.write_file_atomically import write_file_atomically

if TYPE_CHECKING:
    from pathlib import Path


def write_if_unchanged(path: Path, before: str, after: str) -> bool:
    """Write `after` only if the file still holds `before`; False after reporting.

    A file that was missing when read (`before` empty) is created only if it is still
    missing, so one that appeared meanwhile is never overwritten.
    """
    try:
        if before == "" and not path.exists():
            create_file_exclusively(path, after)
        elif backlog_unchanged((path, before)):
            write_file_atomically(path, after)
        else:
            return False
    except FileExistsError:
        print(f"{path}: created meanwhile; nothing written, run again", file=sys.stderr)
        return False
    except OSError as error:
        print(f"{path}: not written ({error}); nothing changed", file=sys.stderr)
        return False
    return True
