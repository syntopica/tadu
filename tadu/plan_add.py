"""Work out the new TODO.md for an added item without writing anything."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.ends_inside_fence import ends_inside_fence
from tadu.insert_item import insert_item
from tadu.introduced_errors import introduced_errors
from tadu.item_lines import item_lines
from tadu.read_text_exact import read_text_exact
from tadu.read_todo_text import read_todo_text
from tadu.split_text_lines import split_text_lines

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.add_request import AddRequest


def plan_add(root: Path, request: AddRequest) -> tuple[str, str, int] | None:
    """(text read, new text, 1-based item line), or None after reporting a refusal."""
    before = read_todo_text(root / "TODO.md")
    if before is None:
        return None
    lines, newline = split_text_lines(before)
    new_lines, index = insert_item(lines, item_lines(request), request.category)
    after = newline.join(new_lines)
    log = root / "TODO_LOG.md"
    log_text = read_text_exact(log) if log.is_file() else ""
    added = introduced_errors((before, log_text), (after, log_text))
    if ends_inside_fence(lines) or added:
        reason = f"would add doctor errors {', '.join(added)}" if added else "a fence is left open"
        print(f"{root / 'TODO.md'}: {reason}; refused", file=sys.stderr)
        return None
    return before, after, index + 1
