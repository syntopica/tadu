"""Decide whether a cached entry still stands for its file."""

from __future__ import annotations

ENTRY_LENGTH = 2


def reusable_payload(entry: object, signature: list[int]) -> list[object] | None:
    """The cached payload when the entry is well formed and its file signature still matches."""
    if isinstance(entry, list) and len(entry) == ENTRY_LENGTH and entry[0] == signature:
        payload = entry[1]
        return payload if isinstance(payload, list) else None
    return None
