"""The changes of several backlogs in a range of days."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from tadu.history_error import HistoryError
from tadu.repository_changes import repository_changes
from tadu.scan_problem import ScanProblem

if TYPE_CHECKING:
    from datetime import date

    from tadu.change_entry import ChangeEntry
    from tadu.change_repository import ChangeRepository


def backlog_changes(
    repositories: tuple[ChangeRepository, ...], since: date, until: date
) -> tuple[list[ChangeEntry], tuple[ScanProblem, ...]]:
    """Every repository's changes from `since` to `until`, newest first by author date.

    A repository git cannot read (not a repository, git missing) is a problem and the others
    are still read. Changes of the same moment keep their repository's order.
    """
    entries: list[ChangeEntry] = []
    problems: list[ScanProblem] = []
    for repository in repositories:
        try:
            entries += repository_changes(repository, since, until)
        except HistoryError as error:
            problems.append(ScanProblem(repository.repository, str(error)))
    entries.sort(key=lambda entry: datetime.fromisoformat(entry["date"] or ""), reverse=True)
    return entries, tuple(problems)
