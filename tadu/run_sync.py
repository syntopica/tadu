"""The sync command."""

from __future__ import annotations

import difflib
import sys
from pathlib import Path

from tadu.block_separator import block_separator
from tadu.convert_newlines import convert_newlines
from tadu.dominant_newline import dominant_newline
from tadu.is_task_backlog import is_task_backlog
from tadu.make_parent_directory import make_parent_directory
from tadu.read_sync_source import read_sync_source
from tadu.replace_rule_block import replace_rule_block
from tadu.rule_block_text import rule_block_text
from tadu.same_ignoring_wrapping import same_ignoring_wrapping
from tadu.sync_target import sync_target
from tadu.task_rule_block_text import task_rule_block_text
from tadu.write_if_unchanged import write_if_unchanged


def run_sync(  # noqa: PLR0913
    path: str, file: str | None, *, write: bool, adopt_legacy: bool, task_backlog: bool = False
) -> int:
    """Print the diff for the rule block; apply it only with write, to the text that was read.

    A new file starts with the opening text its agent needs, such as Cursor's front matter.
    `task_backlog` asks for the format 2 block before todo/tadu.json exists (tadu init).
    """
    root = Path(path)
    if not root.is_dir():
        print(f"{root}: not a directory", file=sys.stderr)
        return 2
    candidate, opening = sync_target(root, file)
    source = read_sync_source(candidate, root)
    if source is None:
        return 2
    target, before = source
    newline = dominant_newline(before)
    text = task_rule_block_text() if task_backlog or is_task_backlog(root) else rule_block_text()
    block = convert_newlines(text, newline)
    after = replace_rule_block(before, block, adopt_legacy=adopt_legacy)
    if after is None:
        start = before or convert_newlines(opening, newline)
        after = start + block_separator(start, newline) + block
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
    saved = not write or (
        make_parent_directory(target) and write_if_unchanged(target, before, after)
    )
    return 0 if saved else 2
