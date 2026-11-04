"""Add an ID paragraph to one item, in memory."""

from __future__ import annotations

from tadu.fenced_lines import fenced_lines
from tadu.id_insert_index import id_insert_index


def insert_id_field(lines: list[str], first: int, uid: str) -> list[str]:
    """The lines with `  ID: uid` as its own paragraph after the item's first paragraph."""
    index = id_insert_index(lines, fenced_lines(lines), first)
    after = lines[index:]
    tail = [""] if after and after[0].strip() else []
    return [*lines[:index], "", f"  ID: {uid}", *tail, *after]
