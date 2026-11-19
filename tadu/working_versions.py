"""The uncommitted changes to a Markdown backlog's files."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.file_versions import FileVersions
from tadu.working_text import working_text

if TYPE_CHECKING:
    from tadu.history_source import HistorySource


def working_versions(source: HistorySource) -> tuple[FileVersions, ...]:
    """Each backlog file whose working tree text differs from HEAD's, HEAD's as its one parent."""
    versions = (
        FileVersions(
            path,
            (source.blobs.read(source.name("HEAD", path)),),
            working_text(source.root / path),
        )
        for path in source.paths
    )
    return tuple(version for version in versions if version.before[0] != version.after)
