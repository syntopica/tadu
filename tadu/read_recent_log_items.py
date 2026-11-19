"""Read the recent closed entries of one backlog's log and its yearly archive."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from tadu.is_recent_entry import is_recent_entry
from tadu.log_archive_years import log_archive_years
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
    """Done and cancelled entries dated on or after the cutoff: the archive's years, then the log.

    The archive (`docs/todo-log/YYYY.md` beside TODO_LOG.md) is the same log split by year, so
    the log's `tadu:log` marker applies to it too; a year before the cutoff's is not read.
    """
    log = root / backlog / "TODO_LOG.md"
    lines = read_text_exact(log).splitlines() if log.is_file() else []
    since, _ = read_log_since(lines, log)
    files = [
        (read_text_exact(file).splitlines(), path)
        for file, path in log_archive_years(root, backlog, cutoff.year)
    ]
    files.append((lines, (PurePosixPath(backlog) / "TODO_LOG.md").as_posix()))
    return tuple(
        item
        for lines_of, path in files
        for item in scan_items(lines_of, repository, path, "x-")
        if is_recent_entry(item.day, since, cutoff)
    )
