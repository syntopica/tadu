"""The changes command."""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING

from tadu.args_scope import args_scope
from tadu.backlog_changes import backlog_changes
from tadu.change_days import change_days
from tadu.change_repositories import change_repositories
from tadu.changes_lines import changes_lines
from tadu.filter_changes import filter_changes
from tadu.history_filter_from_args import history_filter_from_args
from tadu.print_problems import print_problems
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    import argparse
    from datetime import date


def run_changes(args: argparse.Namespace, today: date) -> int:
    """Print what changed across the backlogs from --since to --until (the last 14 days).

    Grouped by event with who made them, or one JSON object per change with --json, newest
    first. Repositories git cannot read go to stderr and do not change the exit code; a bad
    workspace, or a first day after the last, exits 2.
    """
    try:
        since, until = change_days(args.since, args.until, today)
        repositories, unreadable = change_repositories(args_scope(args))
    except (ValueError, WorkspaceError) as error:
        print(f"tadu changes: {error}", file=sys.stderr)
        return 2
    found, problems = backlog_changes(repositories, since, until)
    events = frozenset(event for group in args.event for event in group)
    entries = filter_changes(found, history_filter_from_args(args), events, today)
    if args.json:
        for entry in entries:
            print(json.dumps(entry, ensure_ascii=False))
    else:
        print("\n".join(changes_lines(entries, since, until)))
    print_problems("changes", (*unreadable, *problems))
    return 0
