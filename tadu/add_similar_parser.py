"""Declare the similar subcommand's arguments."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.non_negative_int import non_negative_int

if TYPE_CHECKING:
    import argparse


def add_similar_parser(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add `similar` to the subcommands."""
    similar = commands.add_parser(
        "similar", help="print the items most like a text: check before adding one"
    )
    similar.add_argument("text", help="the title of the item you are about to add")
    similar.add_argument("paths", nargs="*", help="repository roots (default: .)")
    similar.add_argument("--workspace", default=None, help="directory holding tadu-workspace.toml")
    similar.add_argument(
        "--limit", type=non_negative_int, default=5, help="items to print (default 5)"
    )
    similar.add_argument("--open", action="store_true", help="only open items")
