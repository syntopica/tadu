"""List the task files under one backlog folder."""

from __future__ import annotations

import os
from pathlib import Path

from tadu.todo_layout import TASK_SUFFIX


def task_file_paths(folder: Path) -> list[Path]:
    """Every task file below the folder, in path text order; none when the folder is missing.

    Walks with os.walk and sorts plain strings: pathlib's rglob and Path ordering cost seconds
    on a backlog with tens of thousands of closed tasks.
    """
    found = [
        os.path.join(directory, name)  # noqa: PTH118 - plain strings are the fast path here
        for directory, _, names in os.walk(folder)
        for name in names
        if name.endswith(TASK_SUFFIX)
    ]
    found.sort()
    return [Path(text) for text in found]
