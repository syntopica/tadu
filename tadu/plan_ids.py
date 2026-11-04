"""Work out an id request without writing anything."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.assign_ids import assign_ids
from tadu.id_refusal import id_refusal
from tadu.id_targets import id_targets
from tadu.new_task_id import new_task_id
from tadu.read_text_exact import read_text_exact
from tadu.split_text_lines import split_text_lines

if TYPE_CHECKING:
    from pathlib import Path


def plan_ids(root: Path, key: str | None) -> tuple[Path, str, str] | None:
    """TODO.md as (path, text read, text to write); None after reporting a refusal."""
    target = root / "TODO.md"
    if not target.is_file():
        print(f"{target}: missing; start the backlog with `tadu init`", file=sys.stderr)
        return None
    text = read_text_exact(target)
    lines, newline = split_text_lines(text)
    firsts = id_targets(lines, root.resolve().name, key)
    if isinstance(firsts, str):
        print(f"{target}: {firsts}", file=sys.stderr)
        return None
    for first in firsts:
        refusal = id_refusal(text, lines, first)
        if refusal is not None:
            print(f"{target}:{first + 1}: {refusal}; nothing written", file=sys.stderr)
            return None
    return target, text, newline.join(assign_ids(lines, firsts, new_task_id))
