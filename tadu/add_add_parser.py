"""Declare the add subcommand's arguments."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.kinds import KINDS
from tadu.non_negative_int import non_negative_int
from tadu.queues import QUEUES
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
    """Add `add` to the subcommands.

    One command for both formats: a task backlog (todo/tadu.json) takes the task options, any
    other repository an item of TODO.md; repeatable options take one value each time.
    """
    add = commands.add_parser(
        "add",
        help="add a task (format 2, after showing similar ones) or one TODO.md item, such as "
        "a decision for a person (`--kind decision`) met while working alone",
    )
    add.add_argument("path", nargs="?", default=".", help="repository root (default: .)")
    add.add_argument("--title", required=True, help="one line, imperative")
    add.add_argument(
        "--category",
        help="format 1: the ## section, as **Category:**; format 2: category slug (default: general)",
    )
    add.add_argument("--type", help="format 2: type slug (default: untriaged)")
    add.add_argument(
        "--priority",
        choices=TASK_PRIORITIES,
        help="item priority; untriaged is for tasks (format 2: default untriaged)",
    )
    add.add_argument(
        "--kind", choices=KINDS, help="format 1: task, decision, waiting or later (default: none)"
    )
    add.add_argument("--milestone", help="format 2: milestone slug declared in todo/tadu.json")
    add.add_argument("--due", help="deadline, YYYY-MM-DD")
    add.add_argument("--defer-until", help="format 2: not before this day, YYYY-MM-DD")
    add.add_argument("--check-on", help="format 1: YYYY-MM-DD, when to look at it again")
    add.add_argument("--not-before", help="format 1: YYYY-MM-DD, it cannot start before this day")
    add.add_argument("--assignees", help="format 1: comma-separated person ids")
    add.add_argument("--labels", help="format 1: comma-separated labels")
    add.add_argument("--queue", choices=QUEUES, help="ready = can start now")
    add.add_argument("--estimate", type=non_negative_int, help="minutes")
    add.add_argument("--no-id", action="store_true", help="format 1: do not give the item an ID")
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
