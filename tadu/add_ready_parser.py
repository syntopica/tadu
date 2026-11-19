"""Declare the ready subcommand's arguments."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.add_json_argument import add_json_argument
from tadu.add_page_arguments import add_page_arguments

if TYPE_CHECKING:
    import argparse


def add_ready_parser(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add `ready` to the subcommands."""
    ready = commands.add_parser(
        "ready", help="print the open items nothing blocks or defers, most urgent first"
    )
    ready.add_argument("paths", nargs="*", help="repository roots (default: .)")
    ready.add_argument("--workspace", default=None, help="directory holding tadu-workspace.toml")
    add_json_argument(ready, "one JSON object per item")
    add_page_arguments(ready)
