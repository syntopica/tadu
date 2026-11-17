"""Apply one planned change to TODO.md: the shared tail of add and mark."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.backlog_lock import backlog_lock
from tadu.print_diff import print_diff
from tadu.run_doctor import run_doctor
from tadu.write_if_unchanged import write_if_unchanged

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


def run_todo_change(
    root: Path,
    plan: Callable[[], tuple[str, str, int] | None],
    verbs: tuple[str, str],
    *,
    write: bool,
) -> int:
    """Under the lock: plan, print the diff, and with write apply it and run doctor.

    `verbs` is what to say before and after writing, such as ("would add t-1", "added t-1").
    """
    target = root / "TODO.md"
    with backlog_lock(root):
        planned = plan()
        if planned is None:
            return 2
        before, after, line = planned
        if before != after:
            print_diff(str(target), before, after)
        if before == after or not write:
            said = "nothing to change" if before == after else f"{verbs[0]}; run again with --write"
            print(f"{target}:{line}: {said}")
            return 0
        if not write_if_unchanged(target, before, after):
            return 2
    print(f"{target}:{line}: {verbs[1]}")
    return run_doctor((str(root),), as_json=False)
