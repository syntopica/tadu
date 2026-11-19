"""Say which blocks of TODO.md outside its items become untriaged pending tasks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.log_runs import log_runs
from tadu.read_text_exact import read_text_exact

if TYPE_CHECKING:
    from pathlib import Path

SHOWN = 20


def unplaced_report(root: Path) -> str:
    """What to print about the text of TODO.md outside its items; empty when there is none."""
    runs = log_runs(read_text_exact(root / "TODO.md").splitlines())
    if not runs:
        return ""
    found = [f"  TODO.md:{first + 1}: {lines[0].strip()}" for first, lines, _ in runs]
    head = (
        f"tadu migrate: {len(runs)} block(s) of TODO.md outside its items become pending "
        "tasks to triage, each holding its text whole in its notes:"
    )
    more = [f"  ... and {len(found) - SHOWN} more"] if len(found) > SHOWN else []
    return "".join(f"{line}\n" for line in (head, *found[:SHOWN], *more))
