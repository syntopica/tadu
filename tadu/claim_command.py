"""The claim command, for both backlog formats."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.backlog_format import backlog_format
from tadu.markdown_claim import markdown_claim
from tadu.run_claim import run_claim
from tadu.task_format_version import TASK_FORMAT_VERSION
from tadu.with_backlog_lock import with_backlog_lock

if TYPE_CHECKING:
    import argparse
    from datetime import date


def claim_command(args: argparse.Namespace, today: date) -> int:
    """A task backlog claims the task file; TODO.md marks the item in progress for --as.

    A task backlog is claimed under the backlog's lock, taken here: a TODO.md change locks
    itself, and the command must not be locked a second time.
    """
    if backlog_format(args.path) == TASK_FORMAT_VERSION:
        root: str = getattr(args, "root", None) or args.path
        return with_backlog_lock(root, lambda: run_claim(args, today))
    return markdown_claim(args, today)
