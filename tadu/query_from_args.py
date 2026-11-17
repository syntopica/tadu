"""The list query a command line asks for."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from tadu.comma_set import comma_set
from tadu.list_query import ListQuery

if TYPE_CHECKING:
    import argparse


def query_from_args(args: argparse.Namespace) -> ListQuery:
    """Copy the query flags; --text is a case-insensitive regular expression."""
    return ListQuery(
        categories=comma_set(args.category),
        types=comma_set(args.type),
        milestone=args.milestone,
        text=re.compile(args.text, re.IGNORECASE) if args.text else None,
        due_within=args.due_within,
        overdue=args.overdue,
        min_priority=args.min_priority,
        sort=args.sort,
        limit=args.limit,
        offset=args.offset,
    )
