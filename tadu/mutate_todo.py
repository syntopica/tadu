"""The one way to change TODO.md: lock, hash check, atomic write, optional commit."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.backlog_lock import backlog_lock
from tadu.commit_file import commit_file
from tadu.read_text_exact import read_text_exact
from tadu.text_hash import text_hash
from tadu.write_file_atomically import write_file_atomically

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


def mutate_todo(
    root: Path,
    seen_hash: str,
    mutate: Callable[[str], str],
    *,
    commit_message: str | None = None,
) -> str:
    """Apply `mutate` to TODO.md if its hash is `seen_hash`.

    Returns "written", "committed", "stale" (the file moved since the caller read
    it; nothing written) or "commit-failed" (written, git refused).
    shortcut: TODO.md only and no push; `close` writes two files and needs a journal.
    """
    target = root / "TODO.md"
    with backlog_lock(root):
        before = read_text_exact(target)
        if text_hash(before) != seen_hash:
            return "stale"
        write_file_atomically(target, mutate(before))
        if commit_message is None:
            return "written"
        return "committed" if commit_file(root, "TODO.md", commit_message) else "commit-failed"
