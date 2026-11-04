"""Cards for repository roots given without a workspace."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from tadu.build_cards import build_cards
from tadu.read_repository_items import read_repository_items
from tadu.scan_problem import ScanProblem

if TYPE_CHECKING:
    from datetime import date

    from tadu.card import Card


def path_cards(
    roots: tuple[str, ...], cutoff: date
) -> tuple[tuple[Card, ...], tuple[ScanProblem, ...]]:
    """Cards per root, named by directory; unreadable roots become problems."""
    cards: list[Card] = []
    problems: list[ScanProblem] = []
    for text in roots:
        root = Path(text).resolve()
        found = read_repository_items(root, ".", root.name, cutoff)
        if isinstance(found, ScanProblem):
            problems.append(found)
        else:
            cards.extend(build_cards(found, root.name, root, None, None, None))
    return tuple(cards), tuple(problems)
