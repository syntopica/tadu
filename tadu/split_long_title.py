"""Split a tadu v1 title that carries its description."""

from __future__ import annotations

import re

LONG_TITLE = 120
TITLE_LIMIT = 200
SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z`*(])")


def split_long_title(title: str) -> tuple[str, str]:
    """(title, rest): a title over 120 characters keeps its first sentence; the rest opens the notes."""
    if len(title) <= LONG_TITLE:
        return title, ""
    end = SENTENCE_END.search(title[:TITLE_LIMIT])
    if end:
        return title[: end.start()], title[end.end() :]
    if len(title) <= TITLE_LIMIT:
        return title, ""
    head = title[:TITLE_LIMIT].rsplit(" ", 1)[0]
    return head, title[len(head) :].strip()
