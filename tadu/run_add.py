"""The add command: put one new open item into TODO.md."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.plan_add import plan_add
from tadu.run_todo_change import run_todo_change

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.add_request import AddRequest


def run_add(root: Path, request: AddRequest, key: str, *, write: bool) -> int:
    """Print the diff and where the item lands; apply with write, then run doctor."""
    plan = lambda: plan_add(root, request)  # noqa: E731
    return run_todo_change(root, plan, (f"would add {key}", f"added {key}"), write=write)
