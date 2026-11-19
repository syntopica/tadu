"""Command-line entry point: every tadu command, for both backlog formats, and the hook."""

from __future__ import annotations

import sys
from datetime import UTC, datetime

from tadu.build_parser import build_parser
from tadu.command_handlers import command_handlers
from tadu.operations import OPERATIONS
from tadu.quiet_broken_pipe import quiet_broken_pipe
from tadu.target_path import target_path
from tadu.without_gc import without_gc
from tadu.workspace_error import WorkspaceError


def main(argv: list[str] | None = None) -> int:
    """Parse the command line and dispatch to one command.

    A change first settles the one backlog directory it changes, as `args.path`.
    """
    args = build_parser(__doc__).parse_args(argv)
    today = datetime.now(UTC).astimezone().date()
    operation = OPERATIONS[args.command]
    if operation.writes:
        try:
            args.path = target_path(args, operation.access)
        except WorkspaceError as error:
            print(f"tadu {args.command}: {error}", file=sys.stderr)
            return 2
    command = command_handlers(args, today, main)[args.command]
    if args.command in ("board", "mcp"):  # a server: keep collecting garbage
        return quiet_broken_pipe(command)
    return without_gc(lambda: quiet_broken_pipe(command))


if __name__ == "__main__":
    sys.exit(main())
