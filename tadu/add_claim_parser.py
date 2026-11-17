"""Declare the claim subcommand's arguments."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse


def add_claim_parser(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add `claim` to the subcommands."""
    claim = commands.add_parser(
        "claim", help="take a task (format v2): assignee, in progress, started"
    )
    claim.add_argument("id", help="task id or unique prefix")
    claim.add_argument("--as", dest="who", required=True, help="person id or agent:<name>")
    claim.add_argument(
        "--force", action="store_true", help="take over a task someone else has in progress"
    )
    claim.add_argument("--root", default=".", help="repository root (default: .)")
    claim.add_argument("--write", action="store_true", help="write instead of printing the change")
