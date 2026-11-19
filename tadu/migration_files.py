"""The files of a tadu v1 backlog that migrating converts."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.log_archive_years import log_archive_years

if TYPE_CHECKING:
    from pathlib import Path

V1_FILES = ("TODO.md", "TODO_LOG.md")


def migration_files(root: Path) -> tuple[tuple[Path, str], ...]:
    """(file, path relative to root): TODO.md, TODO_LOG.md, then the log's archived years.

    In this order, so the ids derived for items without one do not change when a year is
    archived later; a file that does not exist is left out.
    """
    found = [(root / name, name) for name in V1_FILES if (root / name).is_file()]
    return (*found, *log_archive_years(root, ".", 0))
