"""Work out how to bring everything a format 1 backlog holds into its task backlog."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.canonical_task_text import canonical_task_text
from tadu.completed_tasks import completed_tasks
from tadu.completion_plan import CompletionPlan
from tadu.format_1_header import format_1_header
from tadu.header_config_change import header_config_change
from tadu.load_task_files import load_task_files
from tadu.task_location import task_location
from tadu.task_str import task_str
from tadu.todo_layout import TASK_SUFFIX

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.task_file import TaskFile


def plan_completion(todo: Path, texts: dict[str, str], *, everything: bool) -> CompletionPlan:
    """The file changes completed_tasks asks for, and the headers for tadu.json.

    `texts` are TODO.md and TODO_LOG.md; `everything` when they are still in the repository.
    A file a newer tadu wrote is never rewritten.
    """
    current, stale, refused = completed_tasks(
        load_task_files(todo)[0], texts, everything=everything
    )
    created: list[tuple[Path, str]] = []
    renamed: list[tuple[TaskFile, Path, str | None]] = [*stale]
    rewritten: list[tuple[TaskFile, str]] = []
    for task_id, (file, task) in current.items():
        text = canonical_task_text(task)
        if file is None:
            created.append((task_location(todo, task), text))
        elif text == canonical_task_text(file.task):
            continue
        elif not file.writable:
            refused.append(f"{file.path}: written by a newer tadu format; left as it is")
        elif task_id != task_str(file.task, "id"):
            # path-name: a task file is named by its id
            renamed.append((file, file.path.with_name(f"{task_id}{TASK_SUFFIX}"), text))
        else:
            rewritten.append((file, text))
    config = header_config_change(todo, format_1_header(texts))
    return CompletionPlan(tuple(created), tuple(renamed), tuple(rewritten), config, tuple(refused))
