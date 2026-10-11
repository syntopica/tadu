"""Rewrite every line ending in a text to one style."""

from __future__ import annotations


def convert_newlines(text: str, newline: str) -> str:
    """The text with each CRLF or LF replaced by `newline`."""
    return text.replace("\r\n", "\n").replace("\n", newline)
