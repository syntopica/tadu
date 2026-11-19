"""The todo folder a task file belongs to."""

from __future__ import annotations

from pathlib import PurePosixPath

from tadu.todo_layout import TODO_DIR


def task_todo_folder(path: str) -> str:
    """`<backlog>/todo` of a task file path relative to the checkout, above open/ or archive/.

    The nearest folder named todo; a path outside one gives its own folder.
    """
    file = PurePosixPath(path)
    # path-name: the todo folder, whichever depth of open/, closed/ or archive/ holds the file
    found = next((folder for folder in file.parents if folder.name == TODO_DIR), file.parent)
    return found.as_posix()
