"""Read a tadu command line, with the defaults config files give it."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.apply_config import apply_config
from tadu.build_parser import build_parser
from tadu.config_slots import config_slots

if TYPE_CHECKING:
    import argparse
    from collections.abc import Mapping


def parse_command_line(
    argv: list[str] | None, environ: Mapping[str, str], description: str | None = None
) -> argparse.Namespace:
    """Parse as argparse does; options left out come from config files, then defaults.

    The command line wins over the workspace's local file, which wins over the user's
    config file. argparse exits on a bad command line, and on an option still required
    once the files are read; ConfigError or WorkspaceError for a file that cannot be used.
    """
    parser, commands = build_parser(description)
    slots = config_slots(commands)
    args = parser.parse_args(argv)
    command = slots.get(args.command, {})
    apply_config(args, command, environ)
    missing = [
        s.flag for s in command.values() if s.required and getattr(args, s.action.dest) is None
    ]
    if missing:
        commands[args.command].error(f"the following arguments are required: {', '.join(missing)}")
    return args
