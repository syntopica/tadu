"""Cards for the scope a command was given."""

from __future__ import annotations

from datetime import date, timedelta
from typing import TYPE_CHECKING

from tadu.path_cards import path_cards
from tadu.scope_root import scope_root
from tadu.scope_workspace import scope_workspace
from tadu.workspace_cards import workspace_cards

if TYPE_CHECKING:
    from tadu.card import Card
    from tadu.local_config import LocalConfig
    from tadu.scan_problem import ScanProblem
    from tadu.scope import Scope


def load_cards(
    scope: Scope, done_days: int, today: date
) -> tuple[tuple[Card, ...], tuple[ScanProblem, ...], LocalConfig | None]:
    """Read repository roots or a workspace, only `scope.repository` when given.

    A negative done_days asks for open items only, so no closed ones are read. WorkspaceError
    on a bad scope, such as a repository it does not have.
    """
    cutoff = date.max if done_days < 0 else today - timedelta(days=done_days)
    if scope.workspace is None:
        label = scope_root(scope)[0] if scope.repository is not None else None
        cards, problems = path_cards(scope.paths or (".",), cutoff)
        if label is not None:
            cards = tuple(card for card in cards if card.repository == label)
            problems = tuple(problem for problem in problems if problem.repository == label)
        return cards, problems, None
    loaded, local = scope_workspace(scope)
    cards, problems = workspace_cards(loaded, local, cutoff)
    return cards, problems, local
