"""A task file's versions around one commit."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.blob_reader import BlobReader
    from tadu.git_commit import GitCommit

Version = tuple[str, str] | None


def task_versions(
    commit: GitCommit, prefix: str, blobs: BlobReader
) -> tuple[tuple[Version, ...], Version]:
    """(path, text) of the task in each parent, and after the commit; None where it was absent.

    The commit's files are the task's locations (one pathspec for every folder), so a move,
    which git may record as a delete and an add, pairs the two. Paths are relative to the
    checkout at `prefix`.
    """

    def present(blob: str, path: str) -> Version:
        return (path.removeprefix(prefix), blobs.read(blob)) if blob.strip("0") else None

    after = next((v for c in commit.files if (v := present(c.after, c.path))), None)
    befores = tuple(
        next((v for c in commit.files if (v := present(c.before[n], c.path))), None)
        for n in range(max(len(commit.parents), 1))
    )
    return befores, after
