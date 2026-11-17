"""Declare the mark subcommand's arguments."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.kinds import KINDS
from tadu.mark_states import MARK_STATES
from tadu.priorities import PRIORITIES
from tadu.queues import QUEUES

if TYPE_CHECKING:
    import argparse


def add_mark_parser(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add `mark` to the subcommands."""
    mark = commands.add_parser(
        "mark",
        help="set one open item's state or fields: blocked with the blocker named (such as a decision "
        "added for a person), open again once unblocked, or in_progress",
    )
    mark.add_argument("path", nargs="?", default=".", help="repository root (default: .)")
    mark.add_argument("--match", required=True, help="text found in the item's first line")
    mark.add_argument("--state", choices=tuple(MARK_STATES), help="new state")
    mark.add_argument("--kind", choices=KINDS, help="set the item's Kind:")
    mark.add_argument("--priority", choices=PRIORITIES, help="set the item's Priority:")
    mark.add_argument("--assignees", help="set Assignees: (comma-separated person ids)")
    mark.add_argument("--due", help="set Due: (YYYY-MM-DD)")
    mark.add_argument("--check-on", help="set Check on: (YYYY-MM-DD)")
    mark.add_argument("--not-before", help="set Not before: (YYYY-MM-DD)")
    mark.add_argument("--labels", help="set Labels: (comma-separated)")
    mark.add_argument("--queue", choices=QUEUES, help="set Queue: (backlog or ready)")
    mark.add_argument("--estimate", help="set Estimate: (minutes)")
    mark.add_argument("--note", help="a paragraph added to the item; required for blocked")
    mark.add_argument("--write", action="store_true", help="apply instead of printing the diff")
