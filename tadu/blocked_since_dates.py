"""When each blocked item of one checkout became blocked, read from git blame."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.git_blame_output import git_blame_output
from tadu.line_commit_times import line_commit_times
from tadu.local_date import local_date

if TYPE_CHECKING:
    from datetime import date
    from pathlib import Path

    from tadu.backlog_item import BacklogItem


def blocked_since_dates(items: tuple[BacklogItem, ...], root: Path) -> tuple[date | None, ...]:
    """Per item, the local date its first line last changed if it is `[!]`, else None.

    The `[!]` marker sits on the first line, so that commit is the latest one that
    could have blocked it; an uncommitted line dates from now. Each file is blamed once.
    """
    blamed: dict[str, dict[int, int]] = {}
    dates: list[date | None] = []
    for item in items:
        if item.state != "!":
            dates.append(None)
            continue
        if item.path not in blamed:
            output = git_blame_output(root, item.path)
            blamed[item.path] = line_commit_times(output) if output else {}
        stamp = blamed[item.path].get(item.line)
        dates.append(None if stamp is None else local_date(stamp))
    return tuple(dates)
