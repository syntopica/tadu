"""Declare the paging arguments of a list-style command."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.non_negative_int import non_negative_int

if TYPE_CHECKING:
    import argparse


def add_page_arguments(parser: argparse.ArgumentParser, limit: int = 100) -> None:
    """Add `--limit` (0 = all) and `--offset`."""
    parser.add_argument(
        "--limit",
        type=non_negative_int,
        default=limit,
        help=f"items to print (default {limit}; 0 = all)",
    )
    parser.add_argument("--offset", type=non_negative_int, default=0, help="items to skip")
