"""How `init` and `sync`, which work on an instruction file, are called."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.agent_file import agent_file

if TYPE_CHECKING:
    import argparse
    from datetime import date


def file_command_call(
    args: argparse.Namespace, today: date
) -> tuple[str, tuple[object, ...], dict[str, object]]:
    """The function to run, its positional arguments and its keyword arguments."""
    options: dict[str, object] = {"write": args.write}
    file = args.file
    if args.command == "sync":
        runner = "run_sync"
        options["adopt_legacy"] = args.adopt_legacy
        file = agent_file(args.file, args.agent)
    elif args.format == "2":
        runner = "run_task_init"
    else:
        runner = "run_init"
        options["today"] = today
    return runner, (args.path, file), options
