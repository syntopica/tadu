"""Build the command-line parser: every subcommand and its arguments."""

from __future__ import annotations

import argparse
from importlib.metadata import version

from tadu.add_operation_parser import add_operation_parser
from tadu.intermixed_parser import IntermixedParser
from tadu.operations import OPERATIONS


def build_parser(description: str | None) -> argparse.ArgumentParser:
    """The `tadu` parser with a subcommand for every operation, in the order of OPERATIONS."""
    parser = argparse.ArgumentParser(prog="tadu", description=description)
    parser.add_argument("--version", action="version", version=f"tadu {version('tadu')}")
    commands = parser.add_subparsers(dest="command", required=True, parser_class=IntermixedParser)
    for operation in OPERATIONS.values():
        add_operation_parser(commands, operation)
    return parser
