"""The Markdown lines of a task one change added and removed."""

from __future__ import annotations

from difflib import ndiff
from typing import TYPE_CHECKING

from tadu.task_field_kinds import TASK_LINE_KEYS
from tadu.task_object import task_object

if TYPE_CHECKING:
    from tadu.backlog_item import BacklogItem


def task_line_changes(
    before: BacklogItem | None, after: BacklogItem
) -> tuple[tuple[str, str, str], ...]:
    """(`+` or `-`, key, line) for the notes, done_when and evidence lines, in that order.

    Blank lines are left out; a version that is not a JSON object has no lines.
    """
    old = task_object(before.text if before else None) or {}
    new = task_object(after.text) or {}
    found: list[tuple[str, str, str]] = []
    for key in TASK_LINE_KEYS:
        a, b = old.get(key), new.get(key)
        lines_a = [str(x) for x in a if str(x).strip()] if isinstance(a, list) else []
        lines_b = [str(x) for x in b if str(x).strip()] if isinstance(b, list) else []
        found += [(line[0], key, line[2:]) for line in ndiff(lines_a, lines_b) if line[0] in "+-"]
    return tuple(found)
