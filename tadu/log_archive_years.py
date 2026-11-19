"""The yearly files of a log's archive."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from tadu.log_archive_layout import LOG_ARCHIVE_DIR, LOG_ARCHIVE_YEAR_PATTERN

if TYPE_CHECKING:
    from pathlib import Path


def log_archive_years(root: Path, backlog: str, since_year: int) -> list[tuple[Path, str]]:
    """(file, path relative to root) of each archived year of the backlog's log from since_year.

    Oldest first. Only `docs/todo-log/YYYY.md` files are years; others in the folder are not.
    """
    folder = root.joinpath(backlog, *LOG_ARCHIVE_DIR)
    if not folder.is_dir():
        return []
    found = []
    for file in sorted(folder.iterdir()):
        # path-name: a year file inside the one archive folder, unique within it
        match = LOG_ARCHIVE_YEAR_PATTERN.match(file.name)
        if match and file.is_file() and int(match.group(1)) >= since_year:
            # path-name: the file's own name, under its folder, is its path
            found.append((file, PurePosixPath(backlog, *LOG_ARCHIVE_DIR, file.name).as_posix()))
    return found
