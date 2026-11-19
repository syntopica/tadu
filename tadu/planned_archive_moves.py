"""Plan the moves an archive policy calls for, from task files already read."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from tadu.task_defaults import MONTH_FOLDERS_MIN
from tadu.task_str import task_str
from tadu.todo_layout import ARCHIVE_DIR

if TYPE_CHECKING:
    from datetime import date
    from pathlib import Path

    from tadu.task_file import TaskFile


def planned_archive_moves(
    files: tuple[tuple[TaskFile, ...], tuple[TaskFile, ...]],
    todo: Path,
    policy: dict[str, object],
    today: date,
) -> tuple[tuple[Path, Path], ...]:
    """(from, to) for closed tasks the policy archives, and archived ones a busier year regroups.

    `files` are the task files of closed/ and of archive/. after_days archives tasks closed
    longer ago than that; keep_closed keeps only the newest that many in closed/. A year gets
    month folders (YYYY/MM/) only when its months would hold at least month_folders_min tasks
    on average, counting months that have tasks.
    """
    closed, archived = files
    dated = sorted((task_str(f.task, "closed") or "", f.path) for f in closed if f.writable)
    after, keep = policy.get("after_days"), policy.get("keep_closed")
    moving = set()
    if isinstance(after, int):
        cutoff = (today - timedelta(days=after)).isoformat()
        moving |= {path for day, path in dated if day and day < cutoff}
    if isinstance(keep, int) and len(dated) > keep:
        moving |= {path for _, path in dated[: len(dated) - keep]}
    final = [(path, day) for day, path in dated if path in moving and day]
    final += [
        (f.path, task_str(f.task, "closed") or "") for f in archived if task_str(f.task, "closed")
    ]
    months: dict[str, set[str]] = {}
    for _, day in final:
        months.setdefault(day[:4], set()).add(day[5:7])
    # keys: years taken from the days of the tasks themselves, one entry per year
    counts = {year: sum(1 for _, day in final if day[:4] == year) for year in months}
    need = policy.get("month_folders_min", MONTH_FOLDERS_MIN)
    # keys: years taken from the days of the tasks themselves, one entry per year
    split = {
        year: isinstance(need, int) and counts[year] / len(months[year]) >= need for year in months
    }
    moves = []
    for path, day in final:
        folder = todo / ARCHIVE_DIR / day[:4] / (day[5:7] if split[day[:4]] else "")
        # path-name: both paths sit in one task backlog's own folders, where file names are unique task ids
        if folder / path.name != path:
            # path-name: both paths sit in one task backlog's own folders, where file names are unique task ids
            moves.append((path, folder / path.name))
    return tuple(sorted(moves))
