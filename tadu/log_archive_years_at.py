"""The archived years of a log in one commit."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from tadu.log_archive_layout import LOG_ARCHIVE_DIR, LOG_ARCHIVE_YEAR_PATTERN
from tadu.run_git import run_git

if TYPE_CHECKING:
    from pathlib import Path


def log_archive_years_at(root: Path, commit: str, backlog: str) -> list[str]:
    """The paths (relative to the checkout `root`) of the backlog's archived years, oldest first.

    `backlog` is the backlog's folder relative to root, `.` for root itself.
    """
    folder = PurePosixPath(backlog, *LOG_ARCHIVE_DIR).as_posix()
    listed = run_git(root, ("ls-tree", "--name-only", "-z", commit, "--", f"{folder}/"))
    # path-name: a year file inside the one archive folder, unique within it
    return sorted(
        path
        for path in listed.split("\0")
        if LOG_ARCHIVE_YEAR_PATTERN.match(PurePosixPath(path).name)
    )
