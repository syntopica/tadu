"""Find the repository root a `tadu close` command names."""

from __future__ import annotations


def close_root_word(words: list[str]) -> str | None:
    """The positional root right after `tadu close`, or None when an option comes first."""
    for index in range(len(words) - 2):
        if words[index : index + 2] == ["tadu", "close"] and not words[index + 2].startswith("-"):
            return words[index + 2]
    return None
