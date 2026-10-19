"""Split a text into lines on its own line ending."""

from __future__ import annotations

from tadu.dominant_newline import dominant_newline


def split_text_lines(text: str) -> tuple[list[str], str]:
    """The lines (a trailing newline leaves a final empty one) and the ending to join them with."""
    newline = dominant_newline(text)
    return text.split(newline), newline
