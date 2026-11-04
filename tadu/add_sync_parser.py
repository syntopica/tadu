"""Declare the sync subcommand's arguments."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse


def add_sync_parser(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add `sync` to the subcommands."""
    sync = commands.add_parser("sync", help="write the marked rule block into the instruction file")
    sync.add_argument("path", help="repository root")
    sync.add_argument(
        "--file", default=None, help="instruction file (default: AGENTS.md, else CLAUDE.md)"
    )
    sync.add_argument("--write", action="store_true", help="apply instead of printing the diff")
    sync.add_argument(
        "--adopt-legacy", action="store_true", help="replace an unmarked legacy rule section"
    )
