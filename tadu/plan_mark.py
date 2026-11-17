"""Work out the new TODO.md for a changed item state without writing anything."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.close_refusal import close_refusal
from tadu.introduced_errors import introduced_errors
from tadu.marked_lines import marked_lines
from tadu.read_text_exact import read_text_exact
from tadu.read_todo_text import read_todo_text
from tadu.select_item import select_item
from tadu.split_text_lines import split_text_lines

if TYPE_CHECKING:
    from pathlib import Path


def plan_mark(root: Path, match: str, marker: str, note: str | None) -> tuple[str, str, int] | None:
    """(text read, new text, 1-based item line), or None after reporting a refusal."""
    path = root / "TODO.md"
    before = read_todo_text(path)
    if before is None:
        return None
    lines, newline = split_text_lines(before)
    first = select_item(lines, match, str(path))
    if first is None:
        return None
    log = root / "TODO_LOG.md"
    log_text = read_text_exact(log) if log.is_file() else ""
    after = newline.join(marked_lines(lines, first, marker, note))
    refusal = close_refusal(before, log_text, lines, first) or (
        "would add doctor errors " + ", ".join(added)
        if (added := introduced_errors((before, log_text), (after, log_text)))
        else None
    )
    if refusal is not None:
        print(f"{path}:{first + 1}: {refusal}; refused", file=sys.stderr)
        return None
    return before, after, first + 1
