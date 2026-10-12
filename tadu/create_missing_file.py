"""Create one backlog file only when the repository does not have it yet."""

from __future__ import annotations

import difflib
from typing import TYPE_CHECKING

from tadu.create_file_exclusively import create_file_exclusively

if TYPE_CHECKING:
    from pathlib import Path


def create_missing_file(path: Path, text: str, *, write: bool) -> None:
    """Print the file as a diff and create it with `write`; leave an existing path alone."""
    if path.exists() or path.is_symlink():
        print(f"{path}: exists, left unchanged")
        return
    diff = difflib.unified_diff([], text.splitlines(keepends=True), "/dev/null", str(path))
    print("".join(diff))
    if not write:
        return
    try:
        create_file_exclusively(path, text)
    except FileExistsError:
        print(f"{path}: appeared meanwhile, left unchanged")
