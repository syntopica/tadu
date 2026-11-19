"""Settle the one backlog directory a change is made to."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.operations import OPERATIONS
from tadu.target_path import target_path
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    import argparse


def settle_target(args: argparse.Namespace) -> int | None:
    """Set `args.path` of a change; exit status 2 (printed) when it cannot be told or allowed.

    A command that changes nothing keeps the roots it was given.
    """
    operation = OPERATIONS[args.command]
    if not operation.writes:
        return None
    try:
        args.path = target_path(args, operation.access)
    except WorkspaceError as error:
        print(f"tadu {args.command}: {error}", file=sys.stderr)
        return 2
    return None
