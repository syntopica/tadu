"""Read the recent closed entries of one backlog's log."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from tadu.is_recent_entry import is_recent_entry
from tadu.read_log_since import read_log_since
from tadu.read_text_exact import read_text_exact
from tadu.scan_items import scan_items

if TYPE_CHECKING:
    from datetime import date
    from pathlib import Path

    from tadu.backlog_item import BacklogItem


def read_recent_log_items(
    root: Path, backlog: str, repository: str, cutoff: date
) -> tuple[BacklogItem, ...]:
    """Done and cancelled entries of root/backlog/TODO_LOG.md dated on or after the cutoff."""
    file = root / backlog / "TODO_LOG.md"
    if not file.is_file():
        return ()
    path = (PurePosixPath(backlog) / "TODO_LOG.md").as_posix()
    lines = read_text_exact(file).splitlines()
    since, _ = read_log_since(lines, file)
    items = scan_items(lines, repository, path, "x-")
    return tuple(i for i in items if is_recent_entry(i.day, since, cutoff))
