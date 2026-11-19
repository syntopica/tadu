"""The commits that changed some files."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.git_log_format import GIT_LOG_FORMAT
from tadu.parse_git_log import parse_git_log
from tadu.run_git import run_git

if TYPE_CHECKING:
    from datetime import date
    from pathlib import Path

    from tadu.git_commit import GitCommit

LOG_ARGS = (
    "log",
    "--ignore-missing",
    "--stdin",
    "--date-order",
    "-c",
    "--raw",
    "-z",
    "--root",
    "--no-abbrev",
    "--no-renames",
    "--no-color",
    "--no-show-signature",
    GIT_LOG_FORMAT,
)


def git_log_commits(
    root: Path,
    pathspecs: tuple[str, ...],
    revs: tuple[str, ...] = ("HEAD",),
    since: date | None = None,
) -> tuple[GitCommit, ...]:
    """Commits the revisions select that changed a file the pathspecs (relative to root) match.

    Newest first, never a parent before its children; none in a repository without commits.
    Merges appear when they left a file different from every parent. `since` stops the walk at
    commits committed before that day, on this machine's clock.
    """
    start = (f"--since={since.isoformat()}T00:00:00",) if since else ()
    data = "\n".join((*revs, "--", *pathspecs, ""))
    return parse_git_log(run_git(root, (*LOG_ARGS, *start), data))
