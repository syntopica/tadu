"""Why a recovery from a commit does not run now."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.pending_recovery import pending_recovery
from tadu.recovered_commits import RECOVERED_KEY, recovered_commits

if TYPE_CHECKING:
    from pathlib import Path


def recovery_refusal(todo: Path, commit: str) -> tuple[int, str] | None:
    """(exit status, what to say), or None when the recovery from `commit` may run.

    One already finished from that commit is not redone (exit 0), so what it brought and was
    removed since does not come back; one pending from another commit is finished first (2).
    """
    if commit in recovered_commits(todo):
        return 0, (
            f"already recovered from {commit[:12]}; what it brought and was removed since stays "
            f"removed (drop it from {RECOVERED_KEY} in todo/tadu.json to recover again)"
        )
    pending = pending_recovery(todo)
    if pending not in (None, commit):
        return (
            2,
            f"the recovery from {pending[:12]} has not finished; run it first (--from {pending})",
        )
    return None
