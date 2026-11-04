"""Declare the init subcommand's arguments."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse


def add_init_parser(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add `init` to the subcommands."""
    init = commands.add_parser("init", help="start a tadu backlog in a repository without one")
    init.add_argument("path", nargs="?", default=".", help="repository root (default: .)")
    init.add_argument(
        "--file", default=None, help="instruction file (default: AGENTS.md, else CLAUDE.md)"
    )
    init.add_argument("--write", action="store_true", help="apply instead of printing the diff")
