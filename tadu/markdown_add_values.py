"""The format 1 field values of the task backlog spellings of `tadu add` options."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse


def markdown_add_values(args: argparse.Namespace) -> dict[str, str | None]:
    """not_before, with --defer-until, the task backlog spelling, standing in for it."""
    return {"not_before": args.not_before or args.defer_until}
