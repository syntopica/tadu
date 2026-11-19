"""Drop one line from a task's notes."""

from __future__ import annotations


def without_note(notes: list[object], line: str) -> list[object]:
    """The notes without each `line`, and the blank line that separated it from the one before."""
    kept: list[object] = []
    for note in notes:
        if note != line:
            kept.append(note)
        elif kept and kept[-1] == "":
            kept.pop()
    return kept
