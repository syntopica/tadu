"""Decide whether a recovery runs, and mark it started before it writes anything else."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.mark_recovery import mark_recovery
from tadu.pending_recovery import pending_recovery
from tadu.recovery_refusal import recovery_refusal

if TYPE_CHECKING:
    from pathlib import Path


def start_recovery(todo: Path, commit: str, *, write: bool) -> tuple[int, str] | None:
    """None when the recovery from `commit` goes on, else (exit status, what to say).

    See recovery_refusal. With `write`, tadu.json records the recovery as pending before
    anything else is written, so one that stops or refuses something is never silent: doctor
    reports it (C005) until a run of it finishes and records it as recovered.
    """
    refusal = recovery_refusal(todo, commit)
    if refusal is not None or not write or pending_recovery(todo) == commit:
        return refusal
    problem = mark_recovery(todo, commit)
    return None if problem is None else (2, problem)
