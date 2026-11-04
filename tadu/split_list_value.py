"""Split a comma-separated field value."""

from __future__ import annotations


def split_list_value(value: str) -> tuple[str, ...]:
    """Stripped, non-empty parts of a comma-separated value."""
    return tuple(part.strip() for part in value.split(",") if part.strip())
