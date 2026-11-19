"""The paths in a directory that may be backlog files."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.backlog_file_names import BACKLOG_FILE_NAMES
from tadu.log_archive_layout import LOG_ARCHIVE_DIR, LOG_ARCHIVE_YEAR_PATTERN
from tadu.todo_layout import TODO_DIR

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


def backlog_candidates(directory: Path) -> Iterator[Path]:
    """The backlog and log files, whatever is under `todo/`, and the archived years of the log."""
    yield from (directory / name for name in BACKLOG_FILE_NAMES)
    yield from sorted((directory / TODO_DIR).rglob("*"))
    archive = directory.joinpath(*LOG_ARCHIVE_DIR)
    if archive.is_dir():
        # path-name: a year file inside the one archive folder, as log_archive_years takes it
        yield from (f for f in sorted(archive.iterdir()) if LOG_ARCHIVE_YEAR_PATTERN.match(f.name))
