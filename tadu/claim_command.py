"""The claim command, for both backlog formats."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.backlog_format import backlog_format
from tadu.markdown_claim import markdown_claim
from tadu.run_claim import run_claim
from tadu.task_format_version import TASK_FORMAT_VERSION

if TYPE_CHECKING:
    import argparse
    from datetime import date


def claim_command(args: argparse.Namespace, today: date) -> int:
    """A task backlog claims the task file; TODO.md marks the item in progress for --as."""
    if backlog_format(args.path) == TASK_FORMAT_VERSION:
        return run_claim(args, today)
    return markdown_claim(args, today)
