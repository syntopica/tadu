"""One item line relative to the item's content column."""

from __future__ import annotations


def item_content_line(line: str) -> str:
    """The line without the item's content indent: one leading tab or two spaces."""
    return line[1:] if line[:1] == "\t" else line.removeprefix("  ")
