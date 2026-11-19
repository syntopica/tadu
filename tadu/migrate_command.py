"""Run migrate, its completion or its recovery, from parsed arguments."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from tadu.finish_leftovers import finish_leftovers
from tadu.is_task_backlog import is_task_backlog
from tadu.run_migrate import run_migrate
from tadu.run_recover import run_recover
from tadu.v1_file_names import V1_FILES

if TYPE_CHECKING:
    import argparse


def migrate_command(args: argparse.Namespace) -> int:
    """Recover, finish or migrate, as the repository needs; exit 2 when refused.

    --recover repairs a migrated backlog from git (--from goes only with it); a task backlog
    with TODO.md or TODO_LOG.md beside it is finished; any other repository is migrated.
    """
    root = Path(args.path)
    if args.recover:
        return run_recover(args.path, args.revision, write=args.write)
    if args.revision is not None:
        print("tadu migrate: --from goes with --recover", file=sys.stderr)
        return 2
    if is_task_backlog(root) and any((root / name).is_file() for name in V1_FILES):
        return finish_leftovers(root, write=args.write)
    return run_migrate(args)
