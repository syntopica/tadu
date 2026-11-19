"""How long two texts agree at their end."""

from __future__ import annotations

CHUNK = 4096


def common_suffix_length(a: str, b: str, limit: int) -> int:
    """The number of trailing characters `a` and `b` share, at most `limit`.

    The limit keeps the end from overlapping a common start already counted. Compared a chunk at
    a time, then halving the chunk that differs.
    """
    done = 0
    while done < limit:
        size = min(CHUNK, limit - done)
        if a[len(a) - done - size : len(a) - done] != b[len(b) - done - size : len(b) - done]:
            break
        done += size
    low, high = done, min(done + CHUNK, limit)
    while low < high:
        middle = (low + high + 1) // 2
        if a[len(a) - middle : len(a) - done] == b[len(b) - middle : len(b) - done]:
            low = middle
        else:
            high = middle - 1
    return low
