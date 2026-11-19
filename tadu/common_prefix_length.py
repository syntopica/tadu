"""How long two texts agree from their start."""

from __future__ import annotations

CHUNK = 4096


def common_prefix_length(a: str, b: str) -> int:
    """The number of leading characters `a` and `b` share.

    Compared a chunk at a time, then halving the chunk that differs, so a long file compares at
    the speed of string equality instead of character by character.
    """
    size = min(len(a), len(b))
    at = 0
    while at < size and a[at : at + CHUNK] == b[at : at + CHUNK]:
        at += CHUNK
    low, high = at, min(at + CHUNK, size)
    while low < high:
        middle = (low + high + 1) // 2
        if a[at:middle] == b[at:middle]:
            low = middle
        else:
            high = middle - 1
    return min(low, size)
