"""What a change did to the files of a backlog."""

from __future__ import annotations

from tadu.file_change import FileChange


def file_changes(before: dict[str, bytes], after: dict[str, bytes]) -> list[FileChange]:
    """The files added, changed or deleted, by path.

    A file whose bytes are the same is not a change.
    """
    return [
        FileChange(path, before.get(path), after.get(path))
        for path in sorted(before.keys() | after.keys())
        if before.get(path) != after.get(path)
    ]
