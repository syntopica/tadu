"""Why a backlog cannot be closed by tadu, before anything is computed."""

from __future__ import annotations

from tadu.ends_inside_fence import ends_inside_fence
from tadu.has_irregular_newlines import has_irregular_newlines
from tadu.has_unindented_continuation import has_unindented_continuation
from tadu.item_span_end import item_span_end


def close_refusal(todo_text: str, log_text: str, todo: list[str], first: int) -> str | None:
    """Refuse irregular line endings or ambiguous item boundaries before planning any write."""
    if has_irregular_newlines(todo_text) or has_irregular_newlines(log_text):
        return "irregular line endings (mixed CRLF and LF, a bare CR or a Unicode separator); normalise the file first"
    if ends_inside_fence(todo[first : item_span_end(todo, first)]):
        return "the item opens a fence its indentation does not close; move it by hand"
    if has_unindented_continuation(todo, first):
        return "the item has a possible unindented continuation; indent its full content or move it by hand"
    return None
