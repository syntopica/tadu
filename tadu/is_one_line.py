"""Tell a single line of text."""

from __future__ import annotations


def is_one_line(value: str) -> bool:
    """True when the text holds no line break of any kind."""
    return len(value.splitlines()) <= 1 and not value.endswith(("\n", "\r"))
