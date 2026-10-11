"""The current rule block shipped with the package."""

from __future__ import annotations

from importlib.resources import files


def rule_block_text() -> str:
    """Return the v1 block, markers included, ending in a newline."""
    return files("tadu").joinpath("rule_block_v1.md").read_text(encoding="utf-8")
