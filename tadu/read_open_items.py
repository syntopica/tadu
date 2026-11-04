"""Read the open items of one backlog."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from tadu.read_text_exact import read_text_exact
from tadu.scan_items import scan_items
from tadu.unreadable_file_error import UnreadableFileError

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.backlog_item import BacklogItem


def read_open_items(root: Path, backlog: str, repository: str) -> tuple[BacklogItem, ...]:
    """Open, started and blocked items of root/backlog/TODO.md."""
    file = root / backlog / "TODO.md"
    if not file.is_file():
        raise UnreadableFileError(file, "no TODO.md")
    path = (PurePosixPath(backlog) / "TODO.md").as_posix()
    lines = read_text_exact(file).splitlines()
    return scan_items(lines, repository, path, " ~!")
