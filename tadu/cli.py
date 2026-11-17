"""Command-line entry point: the backlog commands, the task (format v2) commands and the hook."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from tadu.build_parser import build_parser
from tadu.close_command import close_command
from tadu.doctor_command import doctor_command
from tadu.hook_command import hook_command
from tadu.quiet_broken_pipe import quiet_broken_pipe
from tadu.run_add import run_add
from tadu.run_archive import run_archive
from tadu.run_board import run_board
from tadu.run_claim import run_claim
from tadu.run_feed import run_feed
from tadu.run_fmt import run_fmt
from tadu.run_init import run_init
from tadu.run_list import run_list
from tadu.run_migrate import run_migrate
from tadu.run_ready import run_ready
from tadu.run_set import run_set
from tadu.run_show import run_show
from tadu.run_similar import run_similar
from tadu.run_sync import run_sync
from tadu.run_task_init import run_task_init
from tadu.without_gc import without_gc

if TYPE_CHECKING:
    from collections.abc import Callable


def main(argv: list[str] | None = None) -> int:
    """Parse the command line and dispatch to one command."""
    args = build_parser(__doc__).parse_args(argv)
    today = datetime.now(UTC).astimezone().date()
    handlers: dict[str, Callable[[], int]] = {
        "hook": hook_command,
        "close": lambda: close_command(args),
        "init": lambda: (
            run_task_init(args.path, args.file, write=args.write)
            if args.format == "2"
            else run_init(args.path, args.file, write=args.write, today=today)
        ),
        "add": lambda: run_add(args, today),
        "set": lambda: run_set(args, today),
        "claim": lambda: run_claim(args, today),
        "archive": lambda: run_archive(args, today),
        "fmt": lambda: run_fmt(args),
        "migrate": lambda: run_migrate(args),
        "list": lambda: run_list(args, today),
        "show": lambda: run_show(args, today),
        "ready": lambda: run_ready(args, today),
        "similar": lambda: run_similar(args, today),
        "feed": lambda: run_feed(args, today),
        "board": lambda: run_board(args),
        "sync": lambda: run_sync(
            args.path, args.file, write=args.write, adopt_legacy=args.adopt_legacy
        ),
        "doctor": lambda: doctor_command(args, today),
    }
    command = handlers[args.command]
    if args.command == "board":  # a server: keep collecting garbage
        return quiet_broken_pipe(command)
    return without_gc(lambda: quiet_broken_pipe(command))


if __name__ == "__main__":
    sys.exit(main())
