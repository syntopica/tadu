"""Declare the arguments that choose which repositories a command reads."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.non_negative_int import non_negative_int

if TYPE_CHECKING:
    import argparse


def add_scope_arguments(parser: argparse.ArgumentParser) -> None:
    """Add `paths`, `--workspace` and `--done-days`."""
    parser.add_argument("paths", nargs="*", help="repository roots (default: .)")
    parser.add_argument("--workspace", default=None, help="directory holding tadu-workspace.toml")
    parser.add_argument(
        "--done-days",
        type=non_negative_int,
        default=14,
        help="show done and cancelled items this many days back (default: 14)",
    )
