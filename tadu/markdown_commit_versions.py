"""The versions of a Markdown backlog's files one commit changed."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from tadu.file_versions import FileVersions
from tadu.log_archive_layout import LOG_ARCHIVE_DIR, LOG_ARCHIVE_YEAR_PATTERN

if TYPE_CHECKING:
    from tadu.change_source import ChangeSource
    from tadu.git_commit import GitCommit


def markdown_commit_versions(source: ChangeSource, commit: GitCommit) -> tuple[FileVersions, ...]:
    """The backlog's TODO.md, TODO_LOG.md and archived years the commit changed, each version.

    Each file's text in each parent and after it, paths relative to the checkout.
    """
    prefix, blobs = source.prefix, source.blobs
    folder = PurePosixPath(source.backlog)
    names = {(folder / "TODO.md").as_posix(), (folder / "TODO_LOG.md").as_posix()}
    archive = folder.joinpath(*LOG_ARCHIVE_DIR)
    versions: list[FileVersions] = []
    for change in commit.files:
        path = PurePosixPath(change.path.removeprefix(prefix))
        # path-name: a year file directly inside the backlog's one archive folder
        archived = path.parent == archive and LOG_ARCHIVE_YEAR_PATTERN.match(path.name)
        if path.as_posix() in names or archived:
            before = tuple(blobs.read(blob) for blob in change.before)
            versions.append(FileVersions(path.as_posix(), before, blobs.read(change.after)))
    return tuple(versions)
