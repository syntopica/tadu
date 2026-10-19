"""Declare the close subcommand's arguments."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse


def add_close_parser(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add `close` to the subcommands."""
    close = commands.add_parser("close", help="move one open item from TODO.md to TODO_LOG.md")
    close.add_argument("path", nargs="?", default=".", help="repository root (default: .)")
    close.add_argument("--match", required=True, help="text found in the item's first line")
    proof = close.add_mutually_exclusive_group(required=True)
    proof.add_argument("--evidence", help="log it as [x] with this Evidence: line")
    proof.add_argument("--resolution", help="log it as [-] with this Resolution: line")
    close.add_argument("--result", default=None, help="Result: line of the entry")
    close.add_argument("--category", default=None, help="category (default: its ## section)")
    close.add_argument("--title", default=None, help="entry text (default: the item's)")
    close.add_argument("--date", type=date.fromisoformat, default=None, help="YYYY-MM-DD")
    close.add_argument("--write", action="store_true", help="apply instead of printing the diff")
