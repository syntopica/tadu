"""Why a backlog cannot be closed by tadu, before anything is computed."""

from __future__ import annotations

from tadu.ends_inside_fence import ends_inside_fence
from tadu.has_irregular_newlines import has_irregular_newlines
from tadu.item_span_end import item_span_end


def close_refusal(todo_text: str, log_text: str, todo: list[str], first: int) -> str | None:
    """A reason to refuse: irregular line endings, or a fence the item's indentation leaves open."""
    if has_irregular_newlines(todo_text) or has_irregular_newlines(log_text):
        return "irregular line endings (mixed CRLF and LF, a bare CR or a Unicode separator); normalise the file first"
    if ends_inside_fence(todo[first : item_span_end(todo, first)]):
        return "the item opens a fence its indentation does not close; move it by hand"
    return None
