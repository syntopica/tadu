"""Where tadu keeps its item cache."""

from __future__ import annotations

import os
from pathlib import Path

from tadu.item_cache_settings import CACHE_DIR_VARIABLE, NO_CACHE_VARIABLE


def cache_directory() -> Path | None:
    """$TADU_CACHE_DIR, else $XDG_CACHE_HOME/tadu, else ~/.cache/tadu; None when $TADU_NO_CACHE is set.

    Outside the repository on purpose: nothing to ignore in git, and a cloned repository cannot
    ship cache content.
    """
    if os.environ.get(NO_CACHE_VARIABLE):
        return None
    explicit = os.environ.get(CACHE_DIR_VARIABLE)
    if explicit:
        return Path(explicit)
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return Path(base) / "tadu"
