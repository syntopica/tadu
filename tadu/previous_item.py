"""Find what a backlog item was before a change."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.changed_items import changed_items
from tadu.holds_item_text import holds_item_text
from tadu.item_similarity import item_similarity
from tadu.markdown_items import markdown_items

if TYPE_CHECKING:
    from tadu.backlog_item import BacklogItem
    from tadu.file_versions import FileVersions

MIN_SIMILARITY = 0.6


def previous_item(
    versions: tuple[FileVersions, ...], parent: int, new: BacklogItem, repository: str
) -> BacklogItem | None:
    """The item `new` was in one parent of the change; None when the change created it.

    In order: the same text in a file, else the item with the same `ID:` among those the change
    altered or removed, else the most similar of them, of at least MIN_SIMILARITY. An item with
    another `ID:` is never taken for it, so items that closing or a title edit re-keys are
    still followed.
    """
    for version in versions:
        if holds_item_text(version.before[parent], new.text):
            return markdown_items(new.text, repository, version.path)[0]
    olds = [
        old
        for version in versions
        for old in changed_items(version.before[parent], version.after, repository, version.path)
    ]
    same = [old for old in olds if new.fields.id and old.fields.id == new.fields.id]
    if same:
        return same[0]
    scored = [
        (item_similarity(old, new), old) for old in olds if not (new.fields.id and old.fields.id)
    ]
    best = max(scored, key=lambda pair: pair[0], default=None)
    return best[1] if best is not None and best[0] >= MIN_SIMILARITY else None
