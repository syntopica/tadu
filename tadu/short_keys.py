"""Short, unique display forms of task ids."""

from __future__ import annotations

MIN_LENGTH = 10  # "t-" and 8 hex digits, as git shows a commit


def short_keys(keys: tuple[str, ...]) -> dict[str, str]:
    """Each key shortened to the shortest prefix of at least 10 characters no other key shares.

    Only task ids (t-...) are shortened; any other key maps to itself.
    """
    ids = sorted({key for key in keys if key.startswith("t-")})
    # keys: item keys are unique within one list, each maps to its own prefix
    shown = {key: key for key in keys}
    for index, key in enumerate(ids):
        neighbours = ids[max(index - 1, 0) : index] + ids[index + 1 : index + 2]
        common = max(
            (
                next(
                    (n for n, (a, b) in enumerate(zip(key, other, strict=False)) if a != b),
                    len(key),
                )
                for other in neighbours
            ),
            default=0,
        )
        # keys: item keys are unique within one list, each maps to its own prefix
        shown[key] = key[: max(MIN_LENGTH, common + 1)]
    return shown
