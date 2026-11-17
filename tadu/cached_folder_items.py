"""The items of one task folder, from the item cache where the files have not changed."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.cached_payloads import cached_payloads
from tadu.fresh_cache_entry import fresh_cache_entry
from tadu.record_item import record_item

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from tadu.backlog_item import BacklogItem

PAYLOAD_LENGTH = 3


def cached_folder_items(
    folder: Path, root: Path, keep: Callable[[object, object], bool]
) -> list[BacklogItem]:
    """Items of the folder's task files whose raw (state, closed) values `keep` accepts.

    Only kept items are rebuilt from their records; a record that no longer rebuilds (a cache
    written by a different tool version) is read from the file again.
    """
    items: list[BacklogItem] = []
    for name, payload in cached_payloads(
        folder, "items", root, lambda path: fresh_cache_entry(path, root)
    ):
        valid = len(payload) == PAYLOAD_LENGTH
        if valid and not keep(payload[0], payload[1]):
            continue
        try:
            items.append(record_item(payload[2] if valid else None))
        except (TypeError, ValueError):
            fresh = fresh_cache_entry(folder / name, root)
            if fresh is not None and keep(fresh[0], fresh[1]):
                items.append(record_item(fresh[2]))
    return items
