"""Build the command-line parser: every subcommand and its arguments."""

from __future__ import annotations

import argparse

from tadu.add_config_arguments import add_config_arguments
from tadu.add_operation_parser import add_operation_parser
from tadu.intermixed_parser import IntermixedParser
from tadu.operations import OPERATIONS
from tadu.version_action import VersionAction


def build_parser(
    description: str | None,
) -> tuple[argparse.ArgumentParser, dict[str, argparse.ArgumentParser]]:
    """The `tadu` parser, and each subcommand's by name, in the order of OPERATIONS.

    `tadu` and every command take `--config` and `--no-config`.
    """
    parser = argparse.ArgumentParser(prog="tadu", description=description)
    parser.add_argument("--version", action=VersionAction)
    add_config_arguments(parser)
    commands = parser.add_subparsers(dest="command", required=True, parser_class=IntermixedParser)
    for operation in OPERATIONS.values():
        add_operation_parser(commands, operation)
    for command in commands.choices.values():
        add_config_arguments(command)
    return parser, dict(commands.choices)
