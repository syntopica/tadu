"""Name the cache file of one task folder."""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def item_cache_file(directory: Path, kind: str, root: Path, folder: Path) -> Path:
    """The `kind` cache file of one task folder as read from one repository root."""
    where = f"{root.resolve()}\0{folder.resolve()}".encode()
    return directory / f"{kind}-{hashlib.sha256(where).hexdigest()[:24]}.json"
