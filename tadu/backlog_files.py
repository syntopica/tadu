"""The files of a backlog directory, by path inside it."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from tadu.backlog_candidates import backlog_candidates
from tadu.leftover_patterns import MIGRATION_STAGING, REPOSITORY_TEMPORARY

if TYPE_CHECKING:
    from pathlib import Path


def backlog_files(directory: Path) -> dict[str, bytes]:
    """Path (posix, inside the directory) to bytes of what a backlog is made of.

    A temporary file or staging folder of a write that did not finish is not one of them,
    and neither is a link: only regular files are read.
    """
    found: dict[str, bytes] = {}
    for file in backlog_candidates(directory):
        relative = PurePosixPath(file.relative_to(directory).as_posix())
        # path-name: a temporary file is told by its own name, as write_temp_sibling makes it
        leftover = REPOSITORY_TEMPORARY.fullmatch(file.name) or MIGRATION_STAGING in relative.parts
        if file.is_file() and not file.is_symlink() and not leftover:
            # keys: each candidate is a distinct path inside the directory.
            found[relative.as_posix()] = file.read_bytes()
    return found
