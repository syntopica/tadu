"""One version of a task file as an item."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.task_file import TaskFile
from tadu.task_item import task_item
from tadu.task_object import task_object

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.backlog_item import BacklogItem


def task_version_item(root: Path, path: str, text: str) -> BacklogItem:
    """The item of a task file's text at `path` (relative to the checkout `root`).

    A version that is not a JSON object, as a bad commit may have left it, is an item without
    fields; its history shows the text was not valid.
    """
    task = task_object(text) or {}
    return task_item(TaskFile(root / path, text, task, writable=False), root)
