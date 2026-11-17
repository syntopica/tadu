"""Turn the parsed close arguments into a request and run it."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from tadu.close_request_error import close_request_error
from tadu.closing import Closing
from tadu.is_task_backlog import is_task_backlog
from tadu.run_close import run_close
from tadu.run_task_close import run_task_close

if TYPE_CHECKING:
    import argparse


def close_command(args: argparse.Namespace) -> int:
    """Refuse empty or multi-line values with exit 2, otherwise run close."""
    day = args.date or datetime.now(UTC).astimezone().date()
    if is_task_backlog(Path(args.path)):
        return run_task_close(args, day)
    if args.match is None or args.duplicate_of is not None or args.id is not None:
        print(
            "tadu close: a TODO.md backlog needs --match, and takes no --id or --duplicate-of",
            file=sys.stderr,
        )
        return 2
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
        day=day,
    )
    return run_close(args.path, args.match, closing, write=args.write)
