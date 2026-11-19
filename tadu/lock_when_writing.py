"""Hold a backlog's lock around a command that changes it."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.command_runners import LOCKED_COMMANDS
from tadu.with_backlog_lock import with_backlog_lock

if TYPE_CHECKING:
    import argparse
    from collections.abc import Callable


def lock_when_writing(
    name: str, args: argparse.Namespace, run: Callable[[], int]
) -> Callable[[], int]:
    """`run` itself, or `run` under the lock of the backlog at `args.root` (`args.path`)."""
    if name not in LOCKED_COMMANDS:
        return run
    root: str = getattr(args, "root", None) or args.path
    return lambda: with_backlog_lock(root, run)
