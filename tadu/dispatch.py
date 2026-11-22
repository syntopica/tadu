"""Run the one command a parsed command line names."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from tadu.command_runners import DATED_COMMANDS, PLAIN_COMMANDS, SERVER_COMMANDS
from tadu.file_command_call import file_command_call
from tadu.lock_when_writing import lock_when_writing
from tadu.quiet_broken_pipe import quiet_broken_pipe
from tadu.run_command import run_command
from tadu.without_gc import without_gc

if TYPE_CHECKING:
    import argparse
    from collections.abc import Callable


def dispatch(args: argparse.Namespace, main: Callable[[list[str]], int]) -> int:
    """Call the command's function, importing only what it runs; its exit status.

    A server is handed `main`, to run each call as a command line. A change first settles
    the one backlog directory it changes, as `args.path`.
    """
    today = datetime.now(UTC).astimezone().date()
    name: str = args.command
    arguments: tuple[object, ...] = (args,)
    options: dict[str, object] = {}
    if name in DATED_COMMANDS:
        runner, arguments = DATED_COMMANDS[name], (args, today)
    elif name in PLAIN_COMMANDS:
        runner = PLAIN_COMMANDS[name]
    elif name in SERVER_COMMANDS:
        runner, arguments = SERVER_COMMANDS[name], (args, main)
    elif name == "hook":
        runner, arguments = "hook_command", ()
    else:
        runner, arguments, options = file_command_call(args, today)

    def command() -> int:
        return run_command(runner, *arguments, **options)

    command = lock_when_writing(name, args, command)

    if name in SERVER_COMMANDS:  # a server: keep collecting garbage
        return quiet_broken_pipe(command)
    return without_gc(lambda: quiet_broken_pipe(command))
