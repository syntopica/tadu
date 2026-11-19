"""Read the output of `git log -z --raw` in tadu's format."""

from __future__ import annotations

from tadu.git_commit import GitCommit
from tadu.git_log_format import RECORD, UNIT
from tadu.raw_file_change import raw_file_change

SHORT = 10  # hex digits shown for a commit, as for a task id


def parse_git_log(output: str) -> tuple[GitCommit, ...]:
    """The commits, newest first as git printed them.

    Each record is the header, then NUL-separated pairs of a raw line and its path. The short
    form of a commit is its first SHORT hex digits: `-z --no-abbrev` gives full ids only.
    """
    commits: list[GitCommit] = []
    for record in output.split(RECORD)[1:]:
        header, *rest = record.split("\0")
        sha, parents, date, author, subject = header.split(UNIT, 4)
        tokens = [token.strip("\n") for token in rest if token.strip("\n")]
        files = tuple(
            raw_file_change(tokens[at], tokens[at + 1]) for at in range(0, len(tokens) - 1, 2)
        )
        commits.append(
            GitCommit(sha, sha[:SHORT], tuple(parents.split()), date, author, subject, files)
        )
    return tuple(commits)
