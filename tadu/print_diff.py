"""Print a unified diff of one file's proposed change."""

from __future__ import annotations

import difflib


def print_diff(name: str, before: str, after: str) -> None:
    """Write the diff between `before` and `after` to stdout."""
    print(
        "".join(
            difflib.unified_diff(
                before.splitlines(keepends=True), after.splitlines(keepends=True), name, name
            )
        )
    )
