"""Choose the open items an id request gives an ID."""

from __future__ import annotations

from tadu.fenced_lines import fenced_lines
from tadu.item_id import item_id
from tadu.scan_items import scan_items


def id_targets(lines: list[str], repository: str, key: str | None) -> list[int] | str:
    """Line indices of the items to give an ID, or why the request is refused.

    Without a key every open item lacking an ID field is chosen; with one, only
    the item `tadu list` shows under that key, which must lack an ID field.
    """
    fenced = fenced_lines(lines)
    items = scan_items(lines, repository, "TODO.md", " ~!")
    chosen = [item.line - 1 for item in items if key is None or item.key == key]
    if key is not None and not chosen:
        return f"no open item has key {key}"
    missing = [index for index in chosen if item_id(lines, fenced, index) is None]
    if key is not None and not missing:
        return f"the item with key {key} already has an ID"
    return missing
