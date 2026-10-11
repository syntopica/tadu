"""The sync command."""

from __future__ import annotations

import difflib
from pathlib import Path

from tadu.block_separator import block_separator
from tadu.instruction_file import instruction_file
from tadu.replace_rule_block import replace_rule_block
from tadu.rule_block_text import rule_block_text


def run_sync(path: str, file: str | None, write: bool, adopt_legacy: bool) -> int:
    """Print the diff for the rule block; apply it only with write."""
    root = Path(path)
    target = instruction_file(root, file) or root / "AGENTS.md"
    before = target.read_text(encoding="utf-8") if target.is_file() else ""
    block = rule_block_text()
    after = replace_rule_block(before, block, adopt_legacy)
    if after is None:
        after = before + block_separator(before) + block
    if after == before:
        print(f"{target}: up to date")
        return 0
    print(
        "".join(
            difflib.unified_diff(
                before.splitlines(True), after.splitlines(True), str(target), str(target)
            )
        )
    )
    if write:
        target.write_text(after, encoding="utf-8")
    return 0
