"""Locate the repository's canonical instruction file."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def instruction_file(root: Path, explicit: str | None) -> Path | None:
    """The explicit file, else AGENTS.md, else CLAUDE.md, else None."""
    if explicit is not None:
        return root / explicit
    for name in ("AGENTS.md", "CLAUDE.md"):
        if (root / name).is_file():
            return root / name
    return None
