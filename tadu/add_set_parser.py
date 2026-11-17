"""Declare the set subcommand's arguments."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse


def add_set_parser(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add `set` to the subcommands."""
    change = commands.add_parser("set", help="change fields of a task (format v2)")
    change.add_argument("id", help="task id or unique prefix (at least t- and 8 characters)")
    change.add_argument(
        "changes", nargs="+", help="key=value, key+=value or key-=value for lists, key= to remove"
    )
    change.add_argument("--root", default=".", help="repository root (default: .)")
    change.add_argument("--write", action="store_true", help="write instead of printing the change")
