"""Why tadu cannot add an ID to an item."""

from __future__ import annotations

from tadu.has_irregular_newlines import has_irregular_newlines
from tadu.has_unindented_continuation import has_unindented_continuation


def id_refusal(todo_text: str, todo: list[str], first: int) -> str | None:
    """Refuse irregular line endings or an ambiguous item boundary before planning a write."""
    if has_irregular_newlines(todo_text):
        return "irregular line endings (mixed CRLF and LF, a bare CR or a Unicode separator); normalise the file first"
    if has_unindented_continuation(todo, first):
        return "the item has a possible unindented continuation; indent its full content first"
    return None
