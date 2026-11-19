"""Follow a backlog item back through one change."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.holds_item_text import holds_item_text
from tadu.markdown_items import markdown_items
from tadu.previous_item import previous_item

if TYPE_CHECKING:
    from tadu.backlog_item import BacklogItem
    from tadu.file_versions import FileVersions


def item_step(
    versions: tuple[FileVersions, ...], texts: frozenset[tuple[str, str]], repository: str
) -> tuple[tuple[BacklogItem | None, BacklogItem] | None, frozenset[tuple[str, str]]]:
    """(before, after) when the change altered the item, and where to look for it further back.

    `texts` are the (file, text) pairs the item had on the newer side; more than one after a
    merge joined two branches that both changed it. A change that holds none of them after it
    did not touch the item, nor did one that left it as it was in the same file in some
    parent: a merge that took one branch's version is told by that branch's own commits.
    """
    found = [
        (version, text)
        for version in versions
        for path, text in sorted(texts)
        if version.path == path and holds_item_text(version.after, text)
    ]
    if not found:
        return None, texts
    version, text = found[0]
    if any(holds_item_text(before, text) for before in version.before):
        return None, texts
    items = markdown_items(version.after, repository, version.path)
    after = [item for item in items if item.text == text]
    if not after:
        return None, texts
    befores = [
        previous_item(versions, parent, after[0], repository)
        for parent in range(len(version.before))
    ]
    earlier = [before for before in befores if before is not None]
    rest = texts - {(version.path, text)}
    return (earlier[0] if earlier else None, after[0]), rest | {(b.path, b.text) for b in earlier}
