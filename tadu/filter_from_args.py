"""The card filter a list command line asks for."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.card_filter import CardFilter

if TYPE_CHECKING:
    import argparse


def filter_from_args(args: argparse.Namespace) -> CardFilter:
    """Copy the filter flags of the parsed arguments."""
    return CardFilter(
        project=args.project,
        org=args.org,
        role=args.role,
        assignee=args.assignee,
        column=args.column,
        priority=args.priority,
        label=args.label,
        due_before=args.due_before,
        include_cancelled=args.include_cancelled,
    )
