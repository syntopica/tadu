"""Read TODO.md for a change to it."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.has_irregular_newlines import has_irregular_newlines
from tadu.read_text_exact import read_text_exact
from tadu.unreadable_file_error import UnreadableFileError

if TYPE_CHECKING:
    from pathlib import Path


def read_todo_text(path: Path) -> str | None:
    """The exact text; None after reporting a missing, unreadable or irregular file."""
    if not path.is_file():
        print(f"{path}: missing; start the backlog with `tadu init`", file=sys.stderr)
        return None
    try:
        text = read_text_exact(path)
    except UnreadableFileError as error:
        print(f"{path}: {error}; nothing written", file=sys.stderr)
        return None
    if has_irregular_newlines(text):
        print(f"{path}: irregular line endings; normalise the file first", file=sys.stderr)
        return None
    return text
