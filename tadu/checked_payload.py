"""Read and check one task file on its own, as the doctor cache stores it."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.read_task_file import read_task_file
from tadu.task_file_error import TaskFileError
from tadu.task_file_findings import task_file_findings
from tadu.unreadable_file_error import UnreadableFileError

if TYPE_CHECKING:
    from pathlib import Path


def checked_payload(path: Path) -> list[object]:
    """[text, task, writable, findings as [code, severity, line, message], unreadable reason].

    The per-file checks (form, secrets, schema) depend on the file alone, so they are cached
    with it; checks across files and against the configuration run every time.
    """
    try:
        file = read_task_file(path)
    except (TaskFileError, UnreadableFileError) as error:
        return [None, None, False, [], error.reason]
    own = task_file_findings(file)
    findings = [[f.code, f.severity, f.line, f.message] for f in own]
    return [file.text, file.task, file.writable, findings, None]
