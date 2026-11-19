"""Tell cheaply that a commit left a backlog item alone."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.holds_item_text import holds_item_text

if TYPE_CHECKING:
    from tadu.blob_reader import BlobReader
    from tadu.git_commit import GitCommit


def item_kept(
    commit: GitCommit, prefix: str, texts: frozenset[tuple[str, str]], blobs: BlobReader
) -> bool:
    """True when no (file, text) of the item is new in the commit: held after it, in no parent.

    Then the commit did not give the item any of these texts. Only the files the item is in
    are read; `prefix` is the checkout's place in the repository.
    """
    return not any(
        holds_item_text(blobs.read(change.after), text)
        and not any(holds_item_text(blobs.read(blob), text) for blob in change.before)
        for change in commit.files
        for path, text in texts
        if change.path.removeprefix(prefix) == path
    )
