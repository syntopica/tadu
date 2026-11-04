"""Cards for the scope a command was given."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING

from tadu.load_local_config import load_local_config
from tadu.load_workspace import load_workspace
from tadu.path_cards import path_cards
from tadu.workspace_cards import workspace_cards
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    from datetime import date

    from tadu.card import Card
    from tadu.local_config import LocalConfig
    from tadu.scan_problem import ScanProblem


def load_cards(
    paths: tuple[str, ...], workspace: str | None, done_days: int, today: date
) -> tuple[tuple[Card, ...], tuple[ScanProblem, ...], LocalConfig | None]:
    """Read repository roots or a workspace; raise WorkspaceError on a bad scope."""
    cutoff = today - timedelta(days=done_days)
    if workspace is None:
        cards, problems = path_cards(paths or (".",), cutoff)
        return cards, problems, None
    if paths:
        msg = "give repository paths or --workspace, not both"
        raise WorkspaceError(msg)
    directory = Path(workspace)
    loaded = load_workspace(directory)
    local = load_local_config(directory, loaded)
    cards, problems = workspace_cards(loaded, local, cutoff)
    return cards, problems, local
