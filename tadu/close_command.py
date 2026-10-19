"""Turn the parsed close arguments into a request and run it."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from tadu.close_request_error import close_request_error
from tadu.closing import Closing
from tadu.run_close import run_close

if TYPE_CHECKING:
    import argparse


def close_command(args: argparse.Namespace) -> int:
    """Refuse empty or multi-line values with exit 2, otherwise run close."""
    proof = args.evidence if args.evidence is not None else args.resolution
    fields = (args.result, args.category, args.title, proof)
    error = close_request_error(args.match, proof, fields)
    if error is not None:
        print(f"tadu close: {error}", file=sys.stderr)
        return 2
    closing = Closing(
        state="x" if args.evidence is not None else "-",
        proof=proof.strip(),
        result=args.result,
        category=args.category,
        title=args.title,
        day=args.date or datetime.now(UTC).astimezone().date(),
    )
    return run_close(args.path, args.match, closing, write=args.write)
