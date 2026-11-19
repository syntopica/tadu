"""Where tadu keeps its item cache."""

from __future__ import annotations

import os
from pathlib import Path

from platformdirs import user_cache_dir

from tadu.item_cache_settings import CACHE_DIR_VARIABLE, NO_CACHE_VARIABLE


def cache_directory() -> Path | None:
    """$TADU_CACHE_DIR, else the user's cache directory for tadu; None when $TADU_NO_CACHE is set.

    platformdirs knows each system's place: $XDG_CACHE_HOME/tadu or ~/.cache/tadu on Linux,
    ~/Library/Caches/tadu on macOS, %LOCALAPPDATA%/tadu/Cache on Windows. Outside the
    repository on purpose: nothing to ignore in git, and a cloned repository cannot ship
    cache content.
    """
    if os.environ.get(NO_CACHE_VARIABLE):
        return None
    explicit = os.environ.get(CACHE_DIR_VARIABLE)
    if explicit:
        return Path(explicit)
    return Path(user_cache_dir("tadu", appauthor=False))
