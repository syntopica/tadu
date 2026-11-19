"""The items of a backlog file that one change altered or removed."""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from tadu.changed_window import changed_window
from tadu.holds_item_text import holds_item_text
from tadu.markdown_items import ALL_STATES
from tadu.scan_items import scan_items

if TYPE_CHECKING:
    from tadu.backlog_item import BacklogItem


@lru_cache(maxsize=64)
def changed_items(before: str, after: str, repository: str, path: str) -> tuple[BacklogItem, ...]:
    """The items of `before` that `after` does not hold as they were.

    Only the items around what changed are parsed (see changed_window), so a change to one item
    of a long log parses that item, not the log. Recent results are kept: the same pair of
    versions is asked about once per parent and per item a change moved.
    """
    if not before:
        return ()
    items = scan_items(changed_window(before, after).split("\n"), repository, path, ALL_STATES)
    return tuple(item for item in items if not holds_item_text(after, item.text))
