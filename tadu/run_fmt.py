"""The fmt command."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.backlog_unchanged import backlog_unchanged
from tadu.canonical_task_text import canonical_task_text
from tadu.load_task_files import load_task_files
from tadu.task_backlog_dir import task_backlog_dir
from tadu.task_command_error import TaskCommandError
from tadu.write_file_atomically import write_file_atomically

if TYPE_CHECKING:
    import argparse


def run_fmt(args: argparse.Namespace) -> int:
    """Rewrite task files that are not in canonical form; values never change, only the layout.

    Files from a newer format version and files that are not JSON are left alone.
    """
    try:
        todo = task_backlog_dir(args.path)
    except TaskCommandError as error:
        print(f"tadu fmt: {error}", file=sys.stderr)
        return 2
    files, _ = load_task_files(todo)
    changed = [f for f in files if f.writable and f.text != canonical_task_text(f.task)]
    for file in changed:
        print(file.path.relative_to(todo.parent).as_posix())
        if args.write:
            if not backlog_unchanged((file.path, file.text)):
                return 2
            write_file_atomically(file.path, canonical_task_text(file.task))
    verb = "rewrote" if args.write else "would rewrite"
    print(
        f"tadu fmt: {verb} {len(changed)} file(s)"
        + ("" if args.write or not changed else " (dry run: add --write)")
    )
    return 0
