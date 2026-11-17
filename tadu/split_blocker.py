"""Take a v1 blocked item's blocker out of its notes."""

from __future__ import annotations


def split_blocker(notes: list[str]) -> tuple[str, str, list[str]]:
    """(blocker, unblock action, remaining notes) from the first paragraph of the notes.

    The paragraph becomes one line; text after "Smallest unblock:" is the unblock action.
    """
    cut = notes.index("") if "" in notes else len(notes)
    first = " ".join(line.strip() for line in notes[:cut])
    blocker, _, unblock = first.partition("Smallest unblock:")
    action = unblock.strip().rstrip(".")
    action = f"{action[:1].upper()}{action[1:]}." if action else ""
    return blocker.strip() or first, action, notes[cut + 1 :]
