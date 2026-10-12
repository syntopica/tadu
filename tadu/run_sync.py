"""The sync command."""

from __future__ import annotations

import difflib
import sys
from pathlib import Path

from tadu.block_separator import block_separator
from tadu.convert_newlines import convert_newlines
from tadu.dominant_newline import dominant_newline
from tadu.instruction_file import instruction_file
from tadu.read_sync_source import read_sync_source
from tadu.replace_rule_block import replace_rule_block
from tadu.rule_block_text import rule_block_text
from tadu.same_ignoring_wrapping import same_ignoring_wrapping
from tadu.write_file_atomically import write_file_atomically


def run_sync(path: str, file: str | None, *, write: bool, adopt_legacy: bool) -> int:
    """Print the diff for the rule block; apply it only with write."""
    root = Path(path)
    if not root.is_dir():
        print(f"{root}: not a directory", file=sys.stderr)
        return 2
    candidate = instruction_file(root, file) or root / "AGENTS.md"
    source = read_sync_source(candidate, root)
    if source is None:
        return 2
    target, before = source
    newline = dominant_newline(before)
    block = convert_newlines(rule_block_text(), newline)
    after = replace_rule_block(before, block, adopt_legacy=adopt_legacy)
    if after is None:
        after = before + block_separator(before, newline) + block
    if same_ignoring_wrapping(after, before):
        print(f"{candidate}: up to date")
        return 0
    print(
        "".join(
            difflib.unified_diff(
                before.splitlines(keepends=True),
                after.splitlines(keepends=True),
                str(candidate),
                str(candidate),
            )
        )
    )
    if write:
        write_file_atomically(target, after)
    return 0
