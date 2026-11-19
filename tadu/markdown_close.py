"""The close command on a TODO.md backlog."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.close_request_error import close_request_error
from tadu.closing import Closing
from tadu.item_match import item_match
from tadu.run_close import run_close

if TYPE_CHECKING:
    import argparse
    from datetime import date


def markdown_close(args: argparse.Namespace, day: date, today: date) -> int:
    """Move the item --id or --match names to the log on `day`; exit 2 when refused.

    Empty and multi-line values are refused.
    """
    proof = args.evidence if args.evidence is not None else args.resolution
    fields = (args.result, args.category, args.title, proof)
    error = close_request_error(args.match or args.id, proof, fields)
    if error is not None:
        print(f"tadu close: {error}", file=sys.stderr)
        return 2
    match = item_match("close", args, today)
    if match is None:
        return 2
    closing = Closing(
        state="x" if args.evidence is not None else "-",
        proof=proof.strip(),
        result=args.result,
        category=args.category,
        title=args.title,
        day=day,
    )
    return run_close(args.path, match, closing, write=args.write)
