"""Open and recent closed items of one checkout, or the problem."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.read_open_items import read_open_items
from tadu.read_recent_log_items import read_recent_log_items
from tadu.scan_problem import ScanProblem
from tadu.unreadable_file_error import UnreadableFileError

if TYPE_CHECKING:
    from datetime import date
    from pathlib import Path

    from tadu.backlog_item import BacklogItem


def read_repository_items(
    root: Path, backlog: str, repository: str, cutoff: date
) -> tuple[BacklogItem, ...] | ScanProblem:
    """Open items then recent log items, or a ScanProblem when unreadable."""
    if not root.is_dir():
        return ScanProblem(repository, f"checkout {root} is not a directory")
    try:
        return read_open_items(root, backlog, repository) + read_recent_log_items(
            root, backlog, repository, cutoff
        )
    except UnreadableFileError as error:
        return ScanProblem(repository, str(error))
