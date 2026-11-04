"""Declare the id subcommand's arguments."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse


def add_id_parser(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add `id` to the subcommands."""
    ids = commands.add_parser("id", help="give open items of TODO.md without an ID a fresh one")
    ids.add_argument("path", nargs="?", default=".", help="repository root (default: .)")
    ids.add_argument(
        "--key", default=None, help="only the item `tadu list PATH` shows under this key"
    )
    ids.add_argument("--write", action="store_true", help="apply instead of printing the diff")
