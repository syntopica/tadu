"""The archive command."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.archive_moves import archive_moves
from tadu.read_todo_config import read_todo_config
from tadu.task_backlog_dir import task_backlog_dir
from tadu.task_command_error import TaskCommandError
from tadu.task_file_error import TaskFileError
from tadu.todo_layout import ARCHIVE_DIR

if TYPE_CHECKING:
    import argparse
    from datetime import date


def run_archive(args: argparse.Namespace, today: date) -> int:
    """Move old closed tasks to archive/ as todo/tadu.json's policy says; files move unchanged.

    Without a policy nothing moves: a small project keeps only open/ and closed/.
    """
    try:
        todo = task_backlog_dir(args.path)
        policy = read_todo_config(todo).get("archive")
    except (TaskCommandError, TaskFileError) as error:
        print(f"tadu archive: {error}", file=sys.stderr)
        return 2
    if not isinstance(policy, dict):
        print("tadu archive: no archive policy in todo/tadu.json; closed tasks stay in closed/")
        return 0
    moves = archive_moves(todo, policy, today)
    for source, target in moves:
        print(f"{source.relative_to(todo).as_posix()} -> {target.relative_to(todo).as_posix()}")
    print(f"tadu archive: {len(moves)} move(s)" + ("" if args.write else " (dry run: add --write)"))
    if args.write:
        for source, target in moves:
            # writes: archive moves inside one task backlog, planned and shown before --write
            target.parent.mkdir(parents=True, exist_ok=True)
            source.replace(target)
        for folder in sorted((todo / ARCHIVE_DIR).rglob("*"), reverse=True):
            if folder.is_dir() and not any(folder.iterdir()):
                # writes: archive moves inside one task backlog, planned and shown before --write
                folder.rmdir()
    return 0
