"""The versions of a Markdown backlog's files around one commit."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.blob_reader import ABSENT
from tadu.file_versions import FileVersions

if TYPE_CHECKING:
    from tadu.git_commit import GitCommit
    from tadu.history_source import HistorySource


def versions_at(source: HistorySource, commit: GitCommit) -> tuple[FileVersions, ...]:
    """Each backlog file the commit left unlike some parent, in each parent and after it.

    A first commit has one empty parent version. Blob ids are compared first, so a file the
    commit did not change is never read.
    """
    blobs = source.blobs
    versions: list[FileVersions] = []
    for path in source.paths:
        after = blobs.object_id(source.name(commit.sha, path))
        before = tuple(blobs.object_id(source.name(sha, path)) for sha in commit.parents)
        if any(blob != after for blob in before or (ABSENT,)):
            texts = tuple(blobs.read(blob) for blob in before or (ABSENT,))
            versions.append(FileVersions(path, texts, blobs.read(after)))
    return tuple(versions)
