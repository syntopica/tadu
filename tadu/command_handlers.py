"""What each tadu command runs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.claim_command import claim_command
from tadu.close_command import close_command
from tadu.dispatch_add import dispatch_add
from tadu.doctor_command import doctor_command
from tadu.hook_command import hook_command
from tadu.mark_command import mark_command
from tadu.run_archive import run_archive
from tadu.run_board import run_board
from tadu.run_changes import run_changes
from tadu.run_feed import run_feed
from tadu.run_fmt import run_fmt
from tadu.run_inbox import run_inbox
from tadu.run_init import run_init
from tadu.run_list import run_list
from tadu.run_mcp import run_mcp
from tadu.run_migrate import run_migrate
from tadu.run_next import run_next
from tadu.run_prime import run_prime
from tadu.run_ready import run_ready
from tadu.run_set import run_set
from tadu.run_show import run_show
from tadu.run_similar import run_similar
from tadu.run_sync import run_sync
from tadu.run_task_init import run_task_init
from tadu.run_urgent import run_urgent

if TYPE_CHECKING:
    import argparse
    from collections.abc import Callable
    from datetime import date


def command_handlers(
    args: argparse.Namespace, today: date, main: Callable[[list[str]], int]
) -> dict[str, Callable[[], int]]:
    """The command of each operation name, bound to the parsed arguments and the day."""
    return {
        "hook": hook_command,
        "close": lambda: close_command(args, today),
        "mark": lambda: mark_command(args, today),
        "mcp": lambda: run_mcp(args, main),
        "init": lambda: (
            run_task_init(args.path, args.file, write=args.write)
            if args.format == "2"
            else run_init(args.path, args.file, write=args.write, today=today)
        ),
        "add": lambda: dispatch_add(args, today),
        "set": lambda: run_set(args, today),
        "claim": lambda: claim_command(args, today),
        "archive": lambda: run_archive(args, today),
        "fmt": lambda: run_fmt(args),
        "migrate": lambda: run_migrate(args),
        "list": lambda: run_list(args, today),
        "show": lambda: run_show(args, today),
        "changes": lambda: run_changes(args, today),
        "next": lambda: run_next(args, today),
        "inbox": lambda: run_inbox(args, today),
        "urgent": lambda: run_urgent(args, today),
        "prime": lambda: run_prime(args, today),
        "ready": lambda: run_ready(args, today),
        "similar": lambda: run_similar(args, today),
        "feed": lambda: run_feed(args, today),
        "board": lambda: run_board(args, main),
        "sync": lambda: run_sync(
            args.path, args.file, write=args.write, adopt_legacy=args.adopt_legacy
        ),
        "doctor": lambda: doctor_command(args, today),
    }
