"""Read one string field out of a decoded JSON hook payload."""

from __future__ import annotations


def payload_text(payload: object, *keys: str) -> str:
    """The string at `keys` inside nested objects, or "" when any step is missing or not text."""
    value = payload
    for key in keys:
        value = value.get(key) if isinstance(value, dict) else None
    return value if isinstance(value, str) else ""
