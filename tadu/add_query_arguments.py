"""Declare the list command's query arguments."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.add_page_arguments import add_page_arguments
from tadu.non_negative_int import non_negative_int
from tadu.priorities import PRIORITIES

if TYPE_CHECKING:
    import argparse


def add_query_arguments(parser: argparse.ArgumentParser) -> None:
    """Add category, type, milestone, text, date-window, priority, history or open, sort and paging flags."""
    parser.add_argument("--category", help="categories, comma-separated (any of)")
    parser.add_argument("--type", help="task types, comma-separated (any of)")
    parser.add_argument("--milestone", help="milestone slug")
    parser.add_argument("--text", help="case-insensitive regular expression over title and text")
    parser.add_argument(
        "--due-within",
        type=non_negative_int,
        metavar="DAYS",
        help="due within N days, overdue included",
    )
    parser.add_argument("--overdue", action="store_true", help="due before today")
    parser.add_argument("--min-priority", choices=PRIORITIES, help="this priority or more urgent")
    closed = parser.add_mutually_exclusive_group()
    closed.add_argument(
        "--history", action="store_true", help="closed items of all time, not --done-days"
    )
    closed.add_argument(
        "--open",
        action="store_true",
        help="open items only, not --done-days; faster, closed tasks are not read",
    )
    parser.add_argument(
        "--sort",
        default="file",
        choices=("file", "priority", "due", "closed"),
        help="order (default: file)",
    )
    add_page_arguments(parser)
