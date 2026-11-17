"""Declare the add subcommand's arguments."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.kinds import KINDS
from tadu.priorities import PRIORITIES
from tadu.queues import QUEUES

if TYPE_CHECKING:
    import argparse


def add_add_parser(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add `add` to the subcommands."""
    add = commands.add_parser(
        "add",
        help="add one open item to TODO.md, such as a decision for a person "
        "(`--kind decision`) met while working alone",
    )
    add.add_argument("path", nargs="?", default=".", help="repository root (default: .)")
    add.add_argument("--title", required=True, help="the item's first line")
    add.add_argument("--category", help="put it under this ## section, as **Category:**")
    add.add_argument(
        "--kind", choices=KINDS, help="task, decision, waiting or later (default: unclassified)"
    )
    add.add_argument("--priority", choices=PRIORITIES, help="item priority")
    add.add_argument("--assignees", help="comma-separated person ids")
    add.add_argument("--due", help="YYYY-MM-DD: the deadline")
    add.add_argument("--check-on", help="YYYY-MM-DD: when to look at it again or follow up")
    add.add_argument("--not-before", help="YYYY-MM-DD: it cannot be started before this day")
    add.add_argument("--labels", help="comma-separated labels")
    add.add_argument("--queue", choices=QUEUES, help="backlog (default) or ready")
    add.add_argument("--estimate", help="minutes")
    add.add_argument("--note", action="append", help="a paragraph under the title; repeatable")
    add.add_argument("--no-id", action="store_true", help="do not give the item an ID: line")
    add.add_argument("--write", action="store_true", help="apply instead of printing the diff")
