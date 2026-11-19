"""Merge every format 1 item of one id into its task."""

from __future__ import annotations

from functools import reduce

from tadu.merged_task import merged_task


def merged_items(
    task: dict[str, object], items: dict[str, list[dict[str, object]]], *, everything: bool
) -> dict[str, object]:
    """The task with each converted item of its id merged in, in file order (see merged_task)."""

    def merge(into: dict[str, object], item: dict[str, object]) -> dict[str, object]:
        return merged_task(into, item, everything=everything)

    return reduce(merge, items.get(str(task["id"]), []), task)
