"""Insert lines with one blank line separating them from their neighbours."""

from __future__ import annotations


def insert_block(lines: list[str], index: int, block: list[str]) -> list[str]:
    """The lines with `block` at `index`, padded by a blank line wherever a neighbour has text."""
    before, after = lines[:index], lines[index:]
    lead = [""] if before and before[-1].strip() else []
    tail = [""] if after and after[0].strip() else []
    return before + lead + block + tail + after
