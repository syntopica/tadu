"""Declare the add subcommand's arguments."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.non_negative_int import non_negative_int
from tadu.queues import QUEUES
from tadu.task_defaults import UNKNOWN_CATEGORY, UNKNOWN_PRIORITY, UNKNOWN_TYPE
from tadu.task_priorities import TASK_PRIORITIES

if TYPE_CHECKING:
    import argparse

REPEATED = (
    ("--label", "topic slug"),
    ("--assignee", "person id or agent:<name>"),
    ("--blocked-by", "task id or unique prefix that must close first"),
    ("--related", "task id or unique prefix on the same subject"),
    ("--note", 'one Markdown line of the notes ("" is a blank line)'),
    ("--done-when", "one acceptance criterion"),
    ("--link", "URL of a PR, issue or document"),
)


def add_add_parser(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add `add` to the subcommands; repeatable options take one value each time."""
    add = commands.add_parser("add", help="add a task (format v2), after showing similar ones")
    add.add_argument("path", nargs="?", default=".", help="repository root (default: .)")
    add.add_argument("--title", required=True, help="one line, imperative")
    add.add_argument(
        "--category", default=UNKNOWN_CATEGORY, help="category slug (default: general)"
    )
    add.add_argument("--type", default=UNKNOWN_TYPE, help="type slug (default: untriaged)")
    add.add_argument(
        "--priority", default=UNKNOWN_PRIORITY, choices=TASK_PRIORITIES, help="default: untriaged"
    )
    add.add_argument("--milestone", help="milestone slug declared in todo/tadu.json")
    add.add_argument("--due", help="deadline, YYYY-MM-DD")
    add.add_argument("--defer-until", help="not before this day, YYYY-MM-DD")
    add.add_argument("--queue", choices=QUEUES, help="ready = can start now")
    add.add_argument("--estimate", type=non_negative_int, help="minutes")
    add.add_argument("--parent", help="task id or unique prefix of the epic or parent task")
    add.add_argument(
        "--discovered-from", help="task id or unique prefix whose work revealed this one"
    )
    add.add_argument("--created-by", help="person id or agent:<name> (default: $TADU_ACTOR)")
    for flag, text in REPEATED:
        add.add_argument(flag, action="append", help=f"{text}; repeat for more")
    add.add_argument(
        "--write", action="store_true", help="write instead of printing where it would go"
    )
