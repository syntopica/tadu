"""Run doctor from parsed arguments."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.args_scope import args_scope
from tadu.doctor_roots import doctor_roots
from tadu.run_doctor import run_doctor
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    import argparse
    from datetime import date


def doctor_command(args: argparse.Namespace, today: date) -> int:
    """Check the roots given (default `.`), or every repository of a workspace and its items.

    With --repository, only that repository's files. A workspace that does not load is itself
    a finding; any other scope that cannot be read exits 2.
    """
    scope = args_scope(args)
    try:
        roots = doctor_roots(scope)
    except WorkspaceError as error:
        print(f"tadu doctor: {error}", file=sys.stderr)
        return 2
    workspace = scope.workspace if scope.repository is None else None
    return run_doctor(roots, as_json=args.json, workspace=workspace, today=today)
