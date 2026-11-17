"""Write one item cache file."""

from __future__ import annotations

import contextlib
import json
import os
from typing import TYPE_CHECKING

from tadu.item_cache_settings import ITEM_CACHE_VERSION

if TYPE_CHECKING:
    from pathlib import Path


def write_item_cache(path: Path, entries: dict[str, list[object]]) -> None:
    """Replace the cache file in one step; a cache that cannot be written is simply skipped."""
    temporary = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_text(
            json.dumps({"version": ITEM_CACHE_VERSION, "entries": entries}), encoding="utf-8"
        )
        temporary.replace(path)
    except OSError:
        with contextlib.suppress(OSError):
            temporary.unlink(missing_ok=True)
