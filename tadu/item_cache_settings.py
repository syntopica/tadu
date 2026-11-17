"""Names and limits of the git-ignored-by-design item cache (it lives outside the repository)."""

from __future__ import annotations

# Bump when the items built from a task file change shape or meaning: older caches are ignored.
ITEM_CACHE_VERSION = 1
# Files changed this recently are never trusted from the cache: a second write within the
# file system's timestamp resolution could keep the same size and timestamps (as in git's
# "racy clean" problem), so they are re-read until they are older.
RACY_NANOSECONDS = 2_000_000_000
CACHE_DIR_VARIABLE = "TADU_CACHE_DIR"
NO_CACHE_VARIABLE = "TADU_NO_CACHE"
