"""What a directory holds that is not part of a backlog."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def stray_files(directory: Path, known: dict[str, bytes]) -> list[str]:
    """The paths of every file under `directory` that `known` (see backlog_files) lacks.

    Temporary files and staging folders a write left behind are among them.
    """
    return sorted(
        path.relative_to(directory).as_posix()
        for path in directory.rglob("*")
        if (path.is_file() or path.is_symlink())
        and path.relative_to(directory).as_posix() not in known
    )
