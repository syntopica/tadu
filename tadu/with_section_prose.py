"""Add the prose a v1 section carries before its first item to that item's lines."""

from __future__ import annotations


def with_section_prose(block: tuple[str, ...], prose: list[str]) -> tuple[str, ...]:
    """The block with the section's prose as an indented paragraph after the item line.

    A task has no field for section prose, so the first item of the section keeps it in its notes.
    """
    if not prose:
        return block
    return (block[0], "", *(f"  {line}" for line in prose), *block[1:])
