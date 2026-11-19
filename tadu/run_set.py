"""The set command."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.run_task_change import run_task_change

if TYPE_CHECKING:
    import argparse
    from datetime import date


def run_set(args: argparse.Namespace, today: date) -> int:
    """Change fields of one task, validated before writing; exit 2 when refused."""
    return run_task_change("set", args, args.changes, today)
