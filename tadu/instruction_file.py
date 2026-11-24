"""Locate the repository's canonical instruction file."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def instruction_file(root: Path, explicit: str | None) -> Path | None:
    """Honor an explicit target; otherwise use the first agent-discovered instruction file.

    An existing CLAUDE.md block must not hide a higher-precedence AGENTS.md from sync or doctor.
    """
    if explicit is not None:
        return root / explicit
    names = ("AGENTS.override.md", "AGENTS.md", "CLAUDE.md")
    present = [root / name for name in names if (root / name).is_file()]
    chosen = [path for path in present if path.stat().st_size] or present
    return chosen[0] if chosen else None
