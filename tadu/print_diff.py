"""Print the difference between two versions of a file."""

from __future__ import annotations

import difflib
import re

CONTEXT = 3
HUNK = re.compile(r"^@@ -(\d+)(,\d+)? \+(\d+)(,\d+)? @@")


def print_diff(name: str, before: str, after: str) -> None:
    """Write the unified diff between `before` and `after` to stdout.

    The lines both share at the start and at the end (but for CONTEXT lines around the
    change) are set aside before difflib compares the rest, and its line numbers are
    moved back by as much. A change to a log of 25,000 entries is then a few lines
    found at once: compared whole, difflib takes seconds on it, and its heuristic for
    long files (autojunk) can call most of the file changed.
    """
    old, new = before.splitlines(keepends=True), after.splitlines(keepends=True)
    limit = min(len(old), len(new))
    start = next((n for n in range(limit) if old[n] != new[n]), limit)
    end = next((n for n in range(limit - start) if old[-1 - n] != new[-1 - n]), limit - start)
    skip = max(0, start - CONTEXT)
    cut = max(0, end - CONTEXT)
    lines = difflib.unified_diff(old[skip : len(old) - cut], new[skip : len(new) - cut], name, name)

    def renumber(match: re.Match[str]) -> str:
        old_range, new_range = match[2] or "", match[4] or ""
        return f"@@ -{int(match[1]) + skip}{old_range} +{int(match[3]) + skip}{new_range} @@"

    print("".join(HUNK.sub(renumber, line) for line in lines))
