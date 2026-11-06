"""The card filter a list command line asks for."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.card_filter import CardFilter

if TYPE_CHECKING:
    import argparse


def filter_from_args(args: argparse.Namespace, base: CardFilter) -> CardFilter:
    """Copy the filter flags of the parsed arguments; a flag not given keeps the base value."""
    return CardFilter(
        project=base.project if args.project is None else args.project,
        org=base.org if args.org is None else args.org,
        role=base.role if args.role is None else args.role,
        assignee=base.assignee if args.assignee is None else args.assignee,
        column=base.column if args.column is None else args.column,
        priority=base.priority if args.priority is None else args.priority,
        label=base.label if args.label is None else args.label,
        due_before=base.due_before if args.due_before is None else args.due_before,
        include_cancelled=args.include_cancelled or base.include_cancelled,
    )
