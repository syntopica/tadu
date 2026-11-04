"""Command-line entry point: doctor, sync, init, close, list, show and hook."""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from importlib.metadata import version
from typing import TYPE_CHECKING

from tadu.add_close_parser import add_close_parser
from tadu.add_doctor_parser import add_doctor_parser
from tadu.add_init_parser import add_init_parser
from tadu.add_list_parser import add_list_parser
from tadu.add_show_parser import add_show_parser
from tadu.add_sync_parser import add_sync_parser
from tadu.close_command import close_command
from tadu.hook_command import hook_command
from tadu.run_doctor import run_doctor
from tadu.run_init import run_init
from tadu.run_list import run_list
from tadu.run_show import run_show
from tadu.run_sync import run_sync

if TYPE_CHECKING:
    from collections.abc import Callable


def main(argv: list[str] | None = None) -> int:
    """Parse the command line and dispatch to one command."""
    parser = argparse.ArgumentParser(prog="tadu", description=__doc__)
    parser.add_argument("--version", action="version", version=f"tadu {version('tadu')}")
    commands = parser.add_subparsers(dest="command", required=True)
    add_doctor_parser(commands)
    add_sync_parser(commands)
    add_init_parser(commands)
    add_list_parser(commands)
    add_show_parser(commands)
    add_close_parser(commands)
    hook = commands.add_parser("hook", help="agent hooks that run doctor after a backlog change")
    hook.add_argument("agent", choices=["claude"], help="claude: a Claude Code PostToolUse hook")
    args = parser.parse_args(argv)
    today = datetime.now(UTC).astimezone().date()
    handlers: dict[str, Callable[[], int]] = {
        "hook": hook_command,
        "close": lambda: close_command(args),
        "init": lambda: run_init(args.path, args.file, write=args.write, today=today),
        "list": lambda: run_list(args, today),
        "show": lambda: run_show(args, today),
        "sync": lambda: run_sync(
            args.path, args.file, write=args.write, adopt_legacy=args.adopt_legacy
        ),
        "doctor": lambda: run_doctor(tuple(args.paths), as_json=args.json),
    }
    return handlers[args.command]()


if __name__ == "__main__":
    sys.exit(main())
