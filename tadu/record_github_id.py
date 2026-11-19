"""Add one learned GitHub id to the board's file."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.backlog_unchanged import backlog_unchanged
from tadu.create_file_exclusively import create_file_exclusively
from tadu.read_github_ids import read_github_ids
from tadu.render_github_ids import render_github_ids
from tadu.write_file_atomically import write_file_atomically

if TYPE_CHECKING:
    from pathlib import Path


def record_github_id(path: Path, key: str, repository_id: int) -> dict[str, int]:
    """The file's ids once the key's is in it; the file is read afresh first.

    An id another board recorded for the key meanwhile wins and is returned. The file is
    created when missing and otherwise replaced only if unchanged since read, so two
    boards never overwrite each other. Raise OSError when it cannot be written, and
    ValueError when it is unreadable.
    """
    ids, text = read_github_ids(path)
    if key in ids:
        return ids
    ids = {**ids, key: repository_id}
    if text is None:
        create_file_exclusively(path, render_github_ids(ids))
    elif backlog_unchanged((path, text)):
        write_file_atomically(path, render_github_ids(ids))
    else:
        msg = f"{path} changed while the board wrote to it"
        raise OSError(msg)
    return ids
