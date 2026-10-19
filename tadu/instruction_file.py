"""Locate the repository's canonical instruction file."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.holds_rule_markers import holds_rule_markers

if TYPE_CHECKING:
    from pathlib import Path


def instruction_file(root: Path, explicit: str | None) -> Path | None:
    """The explicit file, else the AGENTS.md or CLAUDE.md holding the block, else either one.

    AGENTS.md wins over CLAUDE.md when neither or both hold the block. A tool such as `next dev` can create AGENTS.md beside a CLAUDE.md that already carries
    the block; the block's file stays canonical.
    """
    if explicit is not None:
        return root / explicit
    present = [root / name for name in ("AGENTS.md", "CLAUDE.md") if (root / name).is_file()]
    marked = [path for path in present if holds_rule_markers(path)]
    chosen = marked or present
    return chosen[0] if chosen else None
