"""The rule block for a repository that keeps a task backlog (format v2)."""

from __future__ import annotations

from importlib.resources import files


def task_rule_block_text() -> str:
    """Return the format 2 block, markers included, ending in a newline."""
    return files("tadu").joinpath("rule_block_v5_tasks.md").read_text(encoding="utf-8")
