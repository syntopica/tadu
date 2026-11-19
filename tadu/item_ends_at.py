"""Tell whether an item found in a backlog text stops where its found text does."""

from __future__ import annotations


def item_ends_at(text: str, end: int) -> bool:
    """Whether `end` is at a line end and the next non-blank line, if any, is unindented."""
    at = end
    while at < len(text):
        if text[at] != "\n":
            return False
        after = text.find("\n", at + 1)
        stop = len(text) if after == -1 else after
        line = text[at + 1 : stop]
        if line.strip():
            return line[0] not in " \t"
        at = stop
    return True
