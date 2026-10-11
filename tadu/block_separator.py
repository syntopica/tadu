"""The text that separates prior content from an appended block."""

from __future__ import annotations


def block_separator(before: str, newline: str = "\n") -> str:
    """Return what to add so exactly one blank line precedes the block."""
    if not before:
        return ""
    if before.endswith(newline * 2):
        return ""
    if before.endswith("\n"):
        return newline
    return newline * 2
