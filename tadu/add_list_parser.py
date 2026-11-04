"""Declare the list subcommand's arguments."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from tadu.add_scope_arguments import add_scope_arguments
from tadu.columns import COLUMNS
from tadu.priorities import PRIORITIES

if TYPE_CHECKING:
    import argparse


def add_list_parser(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add `list` to the subcommands."""
    listing = commands.add_parser("list", help="print backlog items as lines or JSON")
    add_scope_arguments(listing)
    listing.add_argument("--json", action="store_true", help="one JSON object per item")
    listing.add_argument("--project", help="project id")
    listing.add_argument("--org", help="organization id")
    listing.add_argument("--role", help="organization role")
    listing.add_argument("--assignee", help="person id")
    listing.add_argument("--column", choices=COLUMNS, help="board column")
    listing.add_argument("--priority", choices=PRIORITIES, help="item priority")
    listing.add_argument("--label", help="item label")
    listing.add_argument("--due-before", type=date.fromisoformat, help="YYYY-MM-DD")
    listing.add_argument("--include-cancelled", action="store_true", help="keep cancelled items")
