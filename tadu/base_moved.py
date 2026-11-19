"""Whether a repository changed under the files a proposal was made from."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.blob_sha import blob_sha

if TYPE_CHECKING:
    from tadu.file_change import FileChange


def base_moved(changes: list[FileChange], remote: dict[str, str]) -> bool:
    """Whether a changed file differs from the one GitHub holds, or is missing on one side.

    A file the change adds must not be on GitHub; one it changes or deletes must hold the
    bytes the change started from.
    """
    return any(
        remote.get(change.path) != (None if change.before is None else blob_sha(change.before))
        for change in changes
    )
