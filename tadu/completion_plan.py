"""The file changes that complete a migration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.task_file import TaskFile


@dataclass(frozen=True)
class CompletionPlan:
    """New task files, renames, files rewritten in place, tadu.json, and what cannot be done.

    A rename is (file under a lost id, path under the real ID, text to write there), the text
    None when a run that stopped already wrote it. `config` is (path, text read, new text).
    """

    created: tuple[tuple[Path, str], ...]
    renamed: tuple[tuple[TaskFile, Path, str | None], ...]
    rewritten: tuple[tuple[TaskFile, str], ...]
    config: tuple[Path, str, str] | None
    refused: tuple[str, ...]
