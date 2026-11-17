"""Declare the mark subcommand's arguments."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.mark_states import MARK_STATES

if TYPE_CHECKING:
    import argparse


def add_mark_parser(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add `mark` to the subcommands."""
    mark = commands.add_parser(
        "mark",
        help="set one open item's state: blocked with the blocker named (such as a decision "
        "added for a person), open again once unblocked, or in_progress",
    )
    mark.add_argument("path", nargs="?", default=".", help="repository root (default: .)")
    mark.add_argument("--match", required=True, help="text found in the item's first line")
    mark.add_argument("--state", required=True, choices=tuple(MARK_STATES), help="new state")
    mark.add_argument("--note", help="a paragraph added to the item; required for blocked")
    mark.add_argument("--write", action="store_true", help="apply instead of printing the diff")
