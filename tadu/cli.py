"""Command-line entry point: every tadu command, for both backlog formats, and the hook."""

from __future__ import annotations

import sys
from datetime import UTC, datetime

from tadu.command_runners import DATED_COMMANDS, PLAIN_COMMANDS, SERVER_COMMANDS
from tadu.file_command_call import file_command_call
from tadu.lock_when_writing import lock_when_writing
from tadu.quiet_broken_pipe import quiet_broken_pipe
from tadu.read_arguments import read_arguments
from tadu.run_command import run_command
from tadu.without_gc import without_gc


def main(argv: list[str] | None = None) -> int:
    """Parse the command line and dispatch to one command, importing only what it runs.

    Options the command line leaves out come from config files; one that cannot be used
    stops the command, exit 2. A change first settles the one backlog directory it changes,
    as `args.path`.
    """
    args = read_arguments(argv, __doc__)
    if isinstance(args, int):
        return args
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


if __name__ == "__main__":
    sys.exit(main())
