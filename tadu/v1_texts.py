"""Read the Markdown files of a format 1 backlog."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.migration_files import migration_files
from tadu.read_text_exact import read_text_exact

if TYPE_CHECKING:
    from pathlib import Path


def v1_texts(root: Path) -> dict[str, str]:
    """Each file migrating converts (see migration_files) by its name, in that order.

    TODO.md and TODO_LOG.md, then the log's archived years, for each of them root holds.
    """
    return {  # keys: a file name appears once in migration_files
        name: read_text_exact(file) for file, name in migration_files(root)
    }
