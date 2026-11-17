"""Split a comma-separated option value."""

from __future__ import annotations


def comma_set(value: str | None) -> frozenset[str]:
    """The non-empty, lowercased parts of the value; empty when the option was not given."""
    return frozenset(part.strip().lower() for part in (value or "").split(",") if part.strip())
