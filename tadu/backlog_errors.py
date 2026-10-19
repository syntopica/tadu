"""The error codes doctor would report for a backlog and log not yet written."""

from __future__ import annotations

import tempfile
from collections import Counter
from pathlib import Path

from tadu.check_log_file import check_log_file
from tadu.check_todo_file import check_todo_file


def backlog_errors(todo: str, log: str) -> Counter[str]:
    """Count each error code the TODO.md and TODO_LOG.md checks find in these texts."""
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch)
        for name, text in (("TODO.md", todo), ("TODO_LOG.md", log)):
            with (root / name).open("w", encoding="utf-8", newline="") as handle:
                handle.write(text)
        findings = check_todo_file(root) + check_log_file(root)
    return Counter(finding.code for finding in findings if finding.severity == "error")
