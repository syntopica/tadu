"""Cut a plural or -ing/-ed ending off one word."""

from __future__ import annotations

from functools import cache

SUFFIXES = ("ing", "ed", "es", "s")
MIN_STEM = 3


@cache
def word_stem(word: str) -> str:
    """The word without its first matching ending, when at least three letters remain (fixes -> fix).

    Cached: similarity tokenises every title of the backlog, and titles share a small vocabulary.
    """
    cut = next((s for s in SUFFIXES if word.endswith(s) and len(word) - len(s) >= MIN_STEM), "")
    return word[: len(word) - len(cut)]
