"""Convert the texts of a format 1 backlog into tasks (format v2)."""

from __future__ import annotations

from tadu.log_runs import log_runs
from tadu.loose_text_task import loose_text_task
from tadu.migration_entries import migration_entries


def converted_tasks(texts: dict[str, str]) -> list[tuple[dict[str, object], str | None, bool]]:
    """(task, category display name, made of loose text) for each, in file order.

    Every item of the files (TODO.md, TODO_LOG.md, then the log's archived years: see
    migration_entries); an id used twice (doctor's F002 in v1) keeps its first task and the
    others get a new stable id. Then each block written outside the items is a task holding
    its text (loose_text_task): an old prose entry of a log a closed one, text of TODO.md
    (which tadu migrate refuses while the file is there) an open one. They come last, so the
    items keep the ids their place gives them.
    """
    found: list[tuple[dict[str, object], str | None, bool]] = [
        (task, shown, False)
        for task, shown, _, _ in migration_entries(
            (name, text.splitlines()) for name, text in texts.items()
        )
    ]
    loose: list[tuple[dict[str, object], str | None, bool]] = [
        (loose_text_task(name, *run), None, True)
        for name, text in texts.items()
        for run in log_runs(text.splitlines())
    ]
    return found + loose
