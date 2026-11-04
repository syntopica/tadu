"""Declare the board subcommand's arguments."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.non_negative_int import non_negative_int

if TYPE_CHECKING:
    import argparse


def add_board_parser(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add `board` to the subcommands."""
    board = commands.add_parser("board", help="serve a read-only kanban page for a workspace")
    board.add_argument("--workspace", required=True, help="directory holding tadu-workspace.toml")
    board.add_argument("--host", default="127.0.0.1", help="address to bind (default: 127.0.0.1)")
    board.add_argument(
        "--port", type=non_negative_int, default=0, help="port to bind (default: 0, any free port)"
    )
    board.add_argument(
        "--done-days",
        type=non_negative_int,
        default=14,
        help="show done and cancelled items this many days back (default: 14)",
    )
