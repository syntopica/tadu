"""Declare the show subcommand's arguments."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.add_scope_arguments import add_scope_arguments

if TYPE_CHECKING:
    import argparse


def add_show_parser(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add `show` to the subcommands."""
    show = commands.add_parser("show", help="print one backlog item by key")
    show.add_argument("key", help="item key")
    add_scope_arguments(show)
    show.add_argument("--json", action="store_true", help="print the item as JSON")
