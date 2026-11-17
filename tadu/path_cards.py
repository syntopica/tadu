"""Cards for repository roots given without a workspace."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.build_cards import build_cards
from tadu.read_repository_items import read_repository_items
from tadu.root_labels import root_labels
from tadu.scan_problem import ScanProblem

if TYPE_CHECKING:
    from datetime import date

    from tadu.card import Card


def path_cards(
    roots: tuple[str, ...], cutoff: date
) -> tuple[tuple[Card, ...], tuple[ScanProblem, ...]]:
    """Cards per distinct root, named as `root_labels` says; unreadable roots become problems."""
    cards: list[Card] = []
    problems: list[ScanProblem] = []
    for label, root in root_labels(roots).items():
        found = read_repository_items(root, ".", label, cutoff)
        if isinstance(found, ScanProblem):
            problems.append(found)
        else:
            cards.extend(build_cards(found, label, root, None, None, None))
    return tuple(cards), tuple(problems)
