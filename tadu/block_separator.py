"""The text that separates prior content from an appended block."""

from __future__ import annotations


def block_separator(before: str) -> str:
    """Return what to add so exactly one blank line precedes the block."""
    if not before:
        return ""
    if before.endswith("\n\n"):
        return ""
    if before.endswith("\n"):
        return "\n"
    return "\n\n"
