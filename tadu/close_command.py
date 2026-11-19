"""Run close for the backlog's format."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.backlog_format import backlog_format
from tadu.format_refusal import format_refusal
from tadu.markdown_close import markdown_close
from tadu.operations import OPERATIONS
from tadu.run_task_close import run_task_close
from tadu.task_format_version import TASK_FORMAT_VERSION
from tadu.with_backlog_lock import with_backlog_lock

if TYPE_CHECKING:
    import argparse
    from datetime import date


def close_command(args: argparse.Namespace, today: date) -> int:
    """Close the item --id or --match names, in either format, on --date (default: today).

    An option only the other format takes exits 2 (see format_refusal). A task backlog is
    closed under the backlog's lock, taken here: the command must not be locked a second time.
    """
    format_ = backlog_format(args.path)
    refusal = format_refusal(OPERATIONS["close"], args, format_)
    if refusal is not None:
        print(f"tadu close: {refusal}", file=sys.stderr)
        return 2
    day = args.date or today
    return (
        with_backlog_lock(args.path, lambda: run_task_close(args, day))
        if format_ == TASK_FORMAT_VERSION
        else markdown_close(args, day, today)
    )
