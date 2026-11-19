"""Compute both new files for a close and refuse one that adds doctor errors."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.close_item import close_item
from tadu.close_plan import ClosePlan
from tadu.finish_close import finish_close
from tadu.fresh_todo_text import fresh_todo_text
from tadu.introduced_errors import introduced_errors
from tadu.logged_entry import logged_entry
from tadu.split_text_lines import split_text_lines

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.closing import Closing


def plan_close(
    root: Path, texts: tuple[str, str], first: int, closing: Closing
) -> ClosePlan | None:
    """The plan for closing the item at line index `first`; an emptied backlog gets the legend.

    An item a stopped close already logged is finished instead: removed, its entry completed.
    """
    todo_text, log_text = texts
    (todo, todo_newline), (log, log_newline) = (
        split_text_lines(todo_text),
        split_text_lines(log_text),
    )
    entry = logged_entry(todo, log, first)
    if entry is None:
        new_todo, new_log = close_item(todo, log, first, closing)
    else:
        finished = finish_close((todo, log), first, entry, closing)
        if isinstance(finished, str):
            print(f"{root / 'TODO.md'}:{first + 1}: {finished}", file=sys.stderr)
            return None
        new_todo, new_log = finished
        print(
            f"{root / 'TODO.md'}:{first + 1}: already logged at TODO_LOG.md:{entry.line} by a "
            "close that stopped halfway; finishing it"
        )
    after_todo = todo_newline.join(new_todo)
    if not after_todo.strip():
        after_todo = todo_newline.join(fresh_todo_text().split("\n"))
    after_log = log_newline.join(new_log)
    added = introduced_errors(texts, (after_todo, after_log))
    if added:
        print(
            f"{root}: closing would add doctor errors {', '.join(added)}; refused", file=sys.stderr
        )
        return None
    todo_path, log_path = root / "TODO.md", root / "TODO_LOG.md"
    return ClosePlan((todo_path, todo_text, after_todo), (log_path, log_text, after_log), first + 1)
