"""Command-line entry point: every tadu command, for both backlog formats, and the hook."""

from __future__ import annotations

import sys

from tadu.dispatch import dispatch
from tadu.newer_format_error import NewerFormatError
from tadu.read_arguments import read_arguments


def main(argv: list[str] | None = None) -> int:
    """Parse the command line and dispatch to one command, importing only what it runs.

    Options the command line leaves out come from config files; one that cannot be used
    stops the command, exit 2, as does a backlog written in a newer format (the hook
    still exits 0, so it never blocks a tool call).
    """
    try:
        args = read_arguments(argv, __doc__)
        return args if isinstance(args, int) else dispatch(args, main)
    except NewerFormatError as error:
        print(f"tadu: {error}", file=sys.stderr)
        return 0 if (sys.argv[1:] if argv is None else argv)[:1] == ["hook"] else 2


if __name__ == "__main__":
    sys.exit(main())
