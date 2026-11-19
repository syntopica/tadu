"""The format 1 field values of the task backlog spellings of `tadu add` options."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.split_list_value import split_list_value
from tadu.unique_in_order import unique_in_order

if TYPE_CHECKING:
    import argparse


def markdown_add_values(args: argparse.Namespace) -> dict[str, str | None]:
    """labels, assignees and not_before, with --label, --assignee and --defer-until joined in."""
    labels = unique_in_order([*split_list_value(args.labels or ""), *(args.label or ())])
    people = unique_in_order([*split_list_value(args.assignees or ""), *(args.assignee or ())])
    return {
        "labels": ", ".join(labels) or None,
        "assignees": ", ".join(people) or None,
        "not_before": args.not_before or args.defer_until,
    }
