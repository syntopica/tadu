"""Declare next, inbox and urgent: the backlog read by who has to act."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.add_attention_arguments import add_attention_arguments
from tadu.non_negative_int import non_negative_int

if TYPE_CHECKING:
    import argparse


def add_attention_parsers(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add `next`, `inbox` and `urgent` to the subcommands."""
    add_attention_arguments(
        commands.add_parser(
            "next",
            help="tasks an agent can do now without a person, most pressing first "
            "(for 'work alone', 'I will be away')",
        ),
        person=True,
    )
    add_attention_arguments(
        commands.add_parser(
            "inbox",
            help="what waits on a person: decisions, due follow-ups and checks, their blocked "
            "tasks (for 'what is waiting for me', 'I am here')",
        ),
        person=True,
    )
    urgent = commands.add_parser(
        "urgent",
        help="urgent or high priority items and items due soon, by who acts (for 'what is urgent')",
    )
    add_attention_arguments(urgent, person=False)
    urgent.add_argument(
        "--days",
        type=non_negative_int,
        default=1,
        help="a date within this many days counts as due soon (default: 1, by tomorrow)",
    )
