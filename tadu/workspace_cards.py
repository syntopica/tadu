"""Cards for every repository of a workspace."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.build_cards import build_cards
from tadu.read_repository_items import read_repository_items
from tadu.scan_problem import ScanProblem

if TYPE_CHECKING:
    from datetime import date

    from tadu.card import Card
    from tadu.local_config import LocalConfig
    from tadu.workspace import Workspace


def workspace_cards(
    workspace: Workspace, local: LocalConfig, cutoff: date
) -> tuple[tuple[Card, ...], tuple[ScanProblem, ...]]:
    """Cards in repository order; unreadable repositories become problems."""
    cards: list[Card] = []
    problems: list[ScanProblem] = []
    for entry in workspace.repositories:
        root = local.paths.get(entry.key)
        if root is None:
            problems.append(ScanProblem(entry.key, "no checkout path in tadu-workspace.local.toml"))
            continue
        found = read_repository_items(root, entry.backlog, entry.key, cutoff)
        if isinstance(found, ScanProblem):
            problems.append(found)
            continue
        project = next((p for p in workspace.projects if entry.key in p.repositories), None)
        cards.extend(build_cards(found, entry.key, root, entry, project, local))
    return tuple(cards), tuple(problems)
