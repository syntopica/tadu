"""The words of a title that count for similarity."""

from __future__ import annotations

import re

from tadu.word_stem import word_stem

STOP_WORDS = frozenset(
    [
        "a",
        "an",
        "the",
        "to",
        "of",
        "in",
        "on",
        "for",
        "and",
        "or",
        "with",
        "from",
        "by",
        "is",
        "are",
        "be",
        "as",
        "at",
        "it",
        "its",
        "this",
        "that",
        "into",
        "we",
        "should",
        "need",
        "todo",
        "our",
        "when",
        "after",
        "before",
    ]
)


WORD = re.compile(r"[a-z0-9]+")


def title_words(text: str) -> tuple[str, ...]:
    """Lowercase words without stop words, with a plural or -ing/-ed ending cut (fixes -> fix)."""
    return tuple(
        word_stem(word)
        for word in WORD.findall(text.lower())
        if len(word) > 1 and word not in STOP_WORDS  # single letters carry no meaning
    )
