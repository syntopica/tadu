"""The sync command."""

from __future__ import annotations

import difflib
import sys
from pathlib import Path

from tadu.block_separator import block_separator
from tadu.convert_newlines import convert_newlines
from tadu.dominant_newline import dominant_newline
from tadu.has_malformed_rule_markers import has_malformed_rule_markers
from tadu.instruction_file import instruction_file
from tadu.read_text_exact import read_text_exact
from tadu.replace_rule_block import replace_rule_block
from tadu.resolve_inside_root import resolve_inside_root
from tadu.rule_block_text import rule_block_text
from tadu.unreadable_file_error import UnreadableFileError
from tadu.write_file_atomically import write_file_atomically


def run_sync(path: str, file: str | None, write: bool, adopt_legacy: bool) -> int:
    """Print the diff for the rule block; apply it only with write."""
    root = Path(path)
    candidate = instruction_file(root, file) or root / "AGENTS.md"
    target = resolve_inside_root(candidate, root)
    if target is None:
        print(f"{candidate}: refusing to write outside {root}", file=sys.stderr)
        return 2
    try:
        before = read_text_exact(target) if target.is_file() else ""
    except UnreadableFileError as error:
        print(f"{candidate} could not be read: {error.reason}", file=sys.stderr)
        return 2
    if has_malformed_rule_markers(before):
        print(f"{candidate}: malformed tadu:rule markers; fix by hand", file=sys.stderr)
        return 2
    newline = dominant_newline(before)
    block = convert_newlines(rule_block_text(), newline)
    after = replace_rule_block(before, block, adopt_legacy)
    if after is None:
        after = before + block_separator(before, newline) + block
    if after == before:
        print(f"{candidate}: up to date")
        return 0
    print(
        "".join(
            difflib.unified_diff(
                before.splitlines(True), after.splitlines(True), str(candidate), str(candidate)
            )
        )
    )
    if write:
        write_file_atomically(target, after)
    return 0
