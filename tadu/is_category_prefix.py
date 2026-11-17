"""Whether a bold `**Label:**` at the start of a legacy item names its category."""

from __future__ import annotations

from tadu.category_prefix_words import CATEGORY_PREFIX_WORDS


def is_category_prefix(label: str) -> bool:
    """A short label (three words at most, no brackets) is a category; a longer one is a title."""
    return len(label.split()) <= CATEGORY_PREFIX_WORDS and not any(mark in label for mark in "()[]")
