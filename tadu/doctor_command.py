"""Run doctor from parsed arguments."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.run_doctor import run_doctor

if TYPE_CHECKING:
    import argparse
    from datetime import date


def doctor_command(args: argparse.Namespace, today: date) -> int:
    """Require repository paths or a workspace, then run doctor."""
    if not args.paths and args.workspace is None:
        print("tadu doctor: give repository paths or --workspace", file=sys.stderr)
        return 2
    return run_doctor(tuple(args.paths), as_json=args.json, workspace=args.workspace, today=today)
