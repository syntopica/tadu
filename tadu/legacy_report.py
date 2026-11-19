"""Say which blocks of a format 1 log become closed tasks of their own."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.log_runs import log_runs
from tadu.v1_texts import v1_texts

if TYPE_CHECKING:
    from pathlib import Path

SHOWN = 20


def legacy_report(root: Path) -> str:
    """What to print about the logs' text outside their dated entries; empty when there is none.

    The logs are TODO_LOG.md and the years archived beside it.
    """
    runs = [
        (name, first, lines)
        for name, text in v1_texts(root).items()
        if name != "TODO.md"
        for first, lines, _ in log_runs(text.splitlines())
    ]
    if not runs:
        return ""
    found = [f"  {name}:{first + 1}: {lines[0].strip()}" for name, first, lines in runs]
    names = ", ".join(sorted({name for name, _, _ in runs}))
    head = (
        f"tadu migrate: {len(runs)} block(s) of {names} outside its dated entries become "
        "closed tasks, each holding its text whole in its notes:"
    )
    more = [f"  ... and {len(found) - SHOWN} more"] if len(found) > SHOWN else []
    return "".join(f"{line}\n" for line in (head, *found[:SHOWN], *more))
