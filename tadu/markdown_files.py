"""The files a Markdown backlog item can live in."""

from __future__ import annotations

from pathlib import PurePosixPath

from tadu.log_archive_layout import LOG_ARCHIVE_DIR


def markdown_files(path: str) -> tuple[str, ...]:
    """TODO.md and TODO_LOG.md of the backlog that holds `path`, relative to the checkout.

    An item in a year of the log's archive (`docs/todo-log/YYYY.md`) came there from the log,
    so that file comes third.
    """
    file = PurePosixPath(path)
    archived = file.parent.parts[-len(LOG_ARCHIVE_DIR) :] == LOG_ARCHIVE_DIR
    folder = file.parents[len(LOG_ARCHIVE_DIR)] if archived else file.parent
    names = ((folder / "TODO.md").as_posix(), (folder / "TODO_LOG.md").as_posix())
    return (*names, path) if archived else names
