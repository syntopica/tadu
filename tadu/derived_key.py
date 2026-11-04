"""Key for an item that has no ID field."""

from __future__ import annotations

import hashlib


def derived_key(repository: str, path: str, title: str, occurrence: int) -> str:
    """A short hash stable across rescans while the file keeps its earlier items."""
    seed = f"{repository}\0{path}\0{title}\0{occurrence}"
    return "k-" + hashlib.sha256(seed.encode()).hexdigest()[:16]
