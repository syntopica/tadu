"""Turn ids or unique prefixes given on the command line into full task ids."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.locate_task import locate_task
from tadu.task_str import task_str

if TYPE_CHECKING:
    from pathlib import Path


def resolve_task_ids(todo: Path, keys: list[str] | None) -> list[str]:
    """The full id of each key, in order; TaskCommandError when one names no task or several."""
    return [task_str(locate_task(todo, key).task, "id") or key for key in keys or ()]
