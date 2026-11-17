"""Read one item cache file."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from tadu.item_cache_settings import ITEM_CACHE_VERSION

if TYPE_CHECKING:
    from pathlib import Path


def read_item_cache(path: Path) -> dict[str, object]:
    """The cached entries by file name; empty when the file is missing, unreadable or of another version."""
    try:
        with path.open(encoding="utf-8") as handle:
            data: object = json.load(handle)
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict) or data.get("version") != ITEM_CACHE_VERSION:
        return {}
    entries = data.get("entries")
    return entries if isinstance(entries, dict) else {}
