"""The open cards and the person an attention command reads."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.args_scope import args_scope
from tadu.load_cards import load_cards

if TYPE_CHECKING:
    import argparse
    from datetime import date

    from tadu.card import Card
    from tadu.scan_problem import ScanProblem


def attention_scope(
    args: argparse.Namespace, today: date
) -> tuple[tuple[Card, ...], tuple[ScanProblem, ...], str | None]:
    """Cards, scan problems and `--person`, else the workspace's `me`; raise WorkspaceError."""
    cards, problems, local = load_cards(args_scope(args), 0, today)
    person = getattr(args, "person", None) or (local.me if local else None)
    return cards, problems, person
