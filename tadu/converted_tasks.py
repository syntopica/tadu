"""Convert the texts of a format 1 backlog into tasks (format v2)."""

from __future__ import annotations

from tadu.log_runs import log_runs
from tadu.loose_text_task import loose_text_task
from tadu.stable_task_id import stable_task_id
from tadu.v1_item_blocks import v1_item_blocks
from tadu.v1_task import v1_task
from tadu.v1_texts import V1_FILES


def converted_tasks(texts: dict[str, str]) -> list[tuple[dict[str, object], str | None, bool]]:
    """(task, category display name, made of loose text) for each, in file order.

    Every item of TODO.md then TODO_LOG.md; an id used twice (doctor's F002 in v1) keeps its
    first task and the others get a new stable id. Then each block written outside the items
    is a task holding its text (loose_text_task): an old prose entry of the log a closed one,
    text of TODO.md (which tadu migrate refuses while the file is there) an open one. They
    come last, so the items keep the ids their place gives them.
    """
    found: list[tuple[dict[str, object], str | None, bool]] = []
    seen: set[object] = set()
    for name in V1_FILES:
        for number, (block, section) in enumerate(v1_item_blocks(texts.get(name, "").splitlines())):
            task, shown = v1_task(block, section, f"{name}:{number}")
            if task["id"] in seen:
                task["id"] = stable_task_id(f"{name}:{number}", str(task["title"]), "repeated id")
            seen.add(task["id"])
            found.append((task, shown, False))
    loose = [
        (loose_text_task(name, *run), None, True)
        for name in V1_FILES
        for run in log_runs(texts.get(name, "").splitlines())
    ]
    return found + loose
