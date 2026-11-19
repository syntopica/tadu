"""Write a planned completion, in the order that lets a stopped run be finished."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.backlog_unchanged import backlog_unchanged
from tadu.create_file_exclusively import create_file_exclusively
from tadu.write_file_atomically import write_file_atomically

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.completion_plan import CompletionPlan


def write_completion(plan: CompletionPlan, removed: tuple[Path, ...]) -> bool:
    """Create, rename, rewrite, update tadu.json, then remove `removed`; OSError when one fails.

    Nothing is written, and False returned after reporting, when a file changed since it was
    read. In that order a run that stops leaves the format 1 files in place, and running it
    again finishes it: every step it repeats finds its work done.
    """
    read = [(file.path, file.text) for file, _ in plan.rewritten]
    read += [(file.path, file.text) for file, _, _ in plan.renamed]
    read += [(plan.config[0], plan.config[1])] if plan.config else []
    if not backlog_unchanged(*read):
        return False
    for path, text in plan.created:
        # writes: the folder of a new task, in a task backlog
        path.parent.mkdir(exist_ok=True)
        create_file_exclusively(path, text)
    for file, target, renamed_text in plan.renamed:
        if renamed_text is not None:
            create_file_exclusively(target, renamed_text)
        # writes: the file under a lost id, once the file under its real ID is written
        file.path.unlink()
    for file, text in plan.rewritten:
        write_file_atomically(file.path, text)
    if plan.config:
        write_file_atomically(plan.config[0], plan.config[2])
    for path in removed:
        # writes: a format 1 file, once the task backlog holds everything it holds
        path.unlink()
    return True
