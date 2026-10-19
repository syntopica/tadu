"""Work out a close without writing anything."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.close_refusal import close_refusal
from tadu.plan_close import plan_close
from tadu.read_backlog import read_backlog
from tadu.select_item import select_item
from tadu.split_text_lines import split_text_lines

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.close_plan import ClosePlan
    from tadu.closing import Closing


def prepare_close(root: Path, match: str, closing: Closing) -> ClosePlan | None:
    """The plan, or None after reporting why the close is refused."""
    texts = read_backlog(root)
    if texts is None:
        return None
    todo, _newline = split_text_lines(texts[0])
    first = select_item(todo, match, str(root / "TODO.md"))
    if first is None:
        return None
    refusal = close_refusal(texts[0], texts[1], todo, first)
    if refusal is not None:
        print(f"{root / 'TODO.md'}:{first + 1}: {refusal}", file=sys.stderr)
        return None
    return plan_close(root, texts, first, closing)
