"""Compare two texts as a prose-wrapping Markdown formatter would leave them."""

from __future__ import annotations

from tadu.markdown_elements import markdown_elements


def same_ignoring_wrapping(left: str, right: str) -> bool:
    """True when the texts differ only in blank lines and soft line wrapping, so a formatter's layout is not drift."""
    return markdown_elements(left) == markdown_elements(right)
