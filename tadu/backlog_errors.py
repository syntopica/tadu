"""The error codes doctor would report for a backlog and log not yet written."""

from __future__ import annotations

import tempfile
from collections import Counter
from pathlib import Path
from typing import TYPE_CHECKING

from tadu.check_log_file import check_log_file
from tadu.check_todo_file import check_todo_file

if TYPE_CHECKING:
    from tadu.finding import Finding


def backlog_errors(todo: str | None, log: str | None) -> Counter[str]:
    """Count each error code the TODO.md and TODO_LOG.md checks find in these texts.

    A text given as None is not checked (see introduced_errors).
    """
    # writes: a throwaway copy in a private temporary directory, removed on exit, so
    #   doctor can check a text that is not on disk yet.
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch)
        findings: tuple[Finding, ...] = ()
        for name, text, check in (
            ("TODO.md", todo, check_todo_file),
            ("TODO_LOG.md", log, check_log_file),
        ):
            if text is None:
                continue
            # writes: into the temporary directory above.
            with (root / name).open("w", encoding="utf-8", newline="") as handle:
                handle.write(text)
            findings += check(root)
    return Counter(finding.code for finding in findings if finding.severity == "error")
