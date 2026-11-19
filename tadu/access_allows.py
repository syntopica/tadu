"""Whether an access level allows what an operation needs."""

from __future__ import annotations

from tadu.access_levels import ACCESS_LEVELS


def access_allows(granted: str, needed: str) -> bool:
    """True when `needed` is read, write or admin and `granted` is that level or above it."""
    return needed in ACCESS_LEVELS and ACCESS_LEVELS.index(needed) <= ACCESS_LEVELS.index(granted)
