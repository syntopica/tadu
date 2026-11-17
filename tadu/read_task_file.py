"""Read one task file."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from tadu.read_text_exact import read_text_exact
from tadu.task_file import TaskFile
from tadu.task_file_error import TaskFileError
from tadu.task_format_version import TASK_FORMAT_VERSION

if TYPE_CHECKING:
    from pathlib import Path


def read_task_file(path: Path) -> TaskFile:
    """The task, writable only when its version is the one this tool writes.

    Raise TaskFileError for text that is not a JSON object with an integer `tadu` version, or
    for a version older than the first JSON version: v1 is Markdown, converted by tadu migrate.
    Later versions will add upgrade steps here, so a newer tool keeps reading older files.
    """
    text = read_text_exact(path)
    try:
        task: object = json.loads(text)
    except ValueError as error:
        raise TaskFileError(path, f"not JSON ({error})") from error
    if not isinstance(task, dict):
        raise TaskFileError(path, "not a JSON object")
    version = task.get("tadu")
    if isinstance(version, bool) or not isinstance(version, int):
        raise TaskFileError(path, "no integer tadu version")
    if version < TASK_FORMAT_VERSION:
        raise TaskFileError(path, f"tadu version {version} is not a task file version")
    return TaskFile(path, text, task, writable=version == TASK_FORMAT_VERSION)
