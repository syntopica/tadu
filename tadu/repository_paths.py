"""A backlog's files, by path in the repository."""

from __future__ import annotations

from pathlib import PurePosixPath


def repository_paths(files: dict[str, bytes], backlog: str) -> dict[str, bytes]:
    """The files with their paths prefixed by the backlog's folder in the repository."""
    # keys: distinct paths inside the backlog stay distinct under one prefix.
    return {PurePosixPath(backlog, path).as_posix(): data for path, data in files.items()}
