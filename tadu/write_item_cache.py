"""Write one item cache file."""

from __future__ import annotations

import contextlib
import json
import os
from typing import TYPE_CHECKING

from tadu.item_cache_settings import ITEM_CACHE_VERSION
from tadu.leftover_patterns import CACHE_TEMPORARY
from tadu.remove_stale_temporaries import remove_stale_temporaries

if TYPE_CHECKING:
    from pathlib import Path


def write_item_cache(path: Path, entries: dict[str, list[object]]) -> None:
    """Replace the cache file in one step; a cache that cannot be written is simply skipped."""
    # path-name: a temporary name next to the one cache file
    temporary = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    try:
        # writes: a derived, git-ignored cache; it is replaced in one step and a failed write is skipped
        path.parent.mkdir(parents=True, exist_ok=True)
        # writes: a derived, git-ignored cache; it is replaced in one step and a failed write is skipped
        temporary.write_text(
            json.dumps({"version": ITEM_CACHE_VERSION, "entries": entries}), encoding="utf-8"
        )
        # writes: a derived, git-ignored cache; it is replaced in one step and a failed write is skipped
        temporary.replace(path)
        remove_stale_temporaries(path.parent, CACHE_TEMPORARY)
    except OSError:
        with contextlib.suppress(OSError):
            # writes: a derived, git-ignored cache; it is replaced in one step and a failed write is skipped
            temporary.unlink(missing_ok=True)
