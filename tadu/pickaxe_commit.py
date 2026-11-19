"""Find the newest commit that changed how often a text occurs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.git_log_format import GIT_LOG_FORMAT
from tadu.parse_git_log import parse_git_log
from tadu.run_git import run_git

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.git_commit import GitCommit

OPTIONS = ("-m", "-n1", "-z", "--no-renames", "--ignore-missing", "--stdin", "--no-color")


def pickaxe_commit(
    root: Path, text: str, tips: tuple[str, ...], pathspecs: tuple[str, ...]
) -> GitCommit | None:
    """The newest commit behind `tips` that changed how often `text` occurs in a matched file.

    Compared with any parent; None when no commit did. Git searches the versions itself
    (`git log -S`), so no version passes through tadu: this is what keeps history fast on a
    long log. The text is attached to its `-S`, so it can never be read as an option. The
    commit comes without its files.
    """
    args = ("log", f"-S{text}", *OPTIONS, "--no-show-signature", GIT_LOG_FORMAT)
    found = parse_git_log(run_git(root, args, "\n".join((*tips, "--", *pathspecs, ""))))
    return found[0] if found else None
