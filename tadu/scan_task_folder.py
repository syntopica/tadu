"""Find the task files under one folder with their file status."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from tadu.todo_layout import TASK_SUFFIX

if TYPE_CHECKING:
    from pathlib import Path


def scan_task_folder(folder: Path, prefix: str = "") -> dict[str, os.stat_result]:
    """Path below the folder (with "/") -> os.stat_result, for every task file; empty when missing.

    One stat per file is what lets the item cache prove an entry is still current.
    """
    found: dict[str, os.stat_result] = {}
    try:
        entries = list(os.scandir(folder))
    except OSError:
        return found
    for entry in entries:
        # path-name: entries of one folder, joined into a path relative to the backlog root
        name = prefix + entry.name
        if entry.is_dir():
            # path-name: entries of one folder, joined into a path relative to the backlog root
            found.update(scan_task_folder(folder / entry.name, name + "/"))
        # path-name: entries of one folder, joined into a path relative to the backlog root
        elif entry.name.endswith(TASK_SUFFIX):
            # keys: relative paths inside one backlog root, unique
            found[name] = entry.stat()
    return found
