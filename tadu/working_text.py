"""A backlog file as it is in the working tree."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.read_text_exact import read_text_exact

if TYPE_CHECKING:
    from pathlib import Path


def working_text(path: Path) -> str:
    """The file's lines joined with line feeds, as git versions are read; empty when it is absent.

    UnreadableFileError when it exists but cannot be read.
    """
    return "\n".join(read_text_exact(path).splitlines()) if path.is_file() else ""
