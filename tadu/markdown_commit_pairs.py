"""What one commit did to the items of a Markdown backlog."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.changed_items import changed_items
from tadu.holds_item_text import holds_item_text
from tadu.previous_item import previous_item

if TYPE_CHECKING:
    from tadu.backlog_item import BacklogItem
    from tadu.file_versions import FileVersions


def markdown_commit_pairs(
    versions: tuple[FileVersions, ...], repository: str
) -> list[tuple[BacklogItem | None, BacklogItem | None]]:
    """(before, after) for each item the change created, altered or removed.

    An item is new after the change when no parent's version of its file holds it as it is,
    so a merge reports only what it made itself, not what a branch brought. Each is paired with
    what it was in the first parent (see previous_item), or with nothing when it was created.
    An item of the first parent that the change left out of every file, and that every parent
    still had, was removed.
    """
    pairs: list[tuple[BacklogItem | None, BacklogItem | None]] = []
    taken: set[tuple[str, str]] = set()
    for version in versions:
        for new in changed_items(version.after, version.before[0], repository, version.path):
            if any(holds_item_text(before, new.text) for before in version.before):
                continue
            old = previous_item(versions, 0, new, repository)
            taken |= {(old.path, old.text)} if old else set()
            pairs.append((old, new))
    for version in versions:
        for old in changed_items(version.before[0], version.after, repository, version.path):
            kept = (old.path, old.text) in taken
            if not kept and all(holds_item_text(before, old.text) for before in version.before):
                pairs.append((old, None))
    return pairs
