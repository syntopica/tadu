"""Read the Markdown files of a format 1 backlog."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.read_text_exact import read_text_exact

if TYPE_CHECKING:
    from pathlib import Path

V1_FILES = ("TODO.md", "TODO_LOG.md")


def v1_texts(root: Path) -> dict[str, str]:
    """TODO.md and TODO_LOG.md by name, for each of them root holds."""
    return {  # keys: the two file names
        name: read_text_exact(root / name) for name in V1_FILES if (root / name).is_file()
    }
