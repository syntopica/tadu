"""A unified diff of what a proposal changes."""

from __future__ import annotations

import difflib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.file_change import FileChange


def change_diff(changes: list[FileChange]) -> str:
    """The changes as one unified diff, `a/` before and `b/` after; /dev/null for a missing side."""
    lines: list[str] = []
    for change in changes:
        before = "" if change.before is None else change.before.decode(errors="replace")
        after = "" if change.after is None else change.after.decode(errors="replace")
        lines += difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            "/dev/null" if change.before is None else f"a/{change.path}",
            "/dev/null" if change.after is None else f"b/{change.path}",
        )
    return "".join(line if line.endswith("\n") else f"{line}\n" for line in lines)
