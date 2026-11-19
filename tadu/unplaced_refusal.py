"""Refuse to migrate a TODO.md that holds text outside its items."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.read_text_exact import read_text_exact
from tadu.unplaced_lines import unplaced_lines

if TYPE_CHECKING:
    from pathlib import Path

SHOWN = 20


def unplaced_refusal(root: Path) -> str | None:
    """Why not, listing each line of TODO.md no task would hold; None when there is none.

    A migration never drops text, and only a person can tell which task a loose line of the
    active backlog belongs to. (The log's loose text becomes closed tasks instead.)
    """
    lines = read_text_exact(root / "TODO.md").splitlines()
    found = [f"  TODO.md:{index + 1}: {lines[index].strip()}" for index in unplaced_lines(lines)]
    if not found:
        return None
    more = [f"  ... and {len(found) - SHOWN} more"] if len(found) > SHOWN else []
    return "\n".join(
        [
            (
                f"{len(found)} line(s) of TODO.md are in no item, and no task would hold them; "
                "move each into an item (indented under it) or into a new item, then run again:"
            ),
            *found[:SHOWN],
            *more,
        ]
    )
