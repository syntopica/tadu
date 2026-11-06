"""The JSON the board page renders."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from tadu.card_json import card_json
from tadu.columns import COLUMNS
from tadu.load_local_config import load_local_config
from tadu.load_workspace import load_workspace
from tadu.workspace_cards import workspace_cards
from tadu.workspace_id import workspace_id
from tadu.workspace_structure import workspace_structure

if TYPE_CHECKING:
    from datetime import date

    from tadu.board_state import BoardState


def board_payload(state: BoardState, today: date) -> dict[str, object]:
    """Re-scan the workspace; raise WorkspaceError when it no longer loads."""
    loaded = load_workspace(state.workspace)
    local = load_local_config(state.workspace, loaded)
    cutoff = today - timedelta(days=state.done_days)
    cards, problems = workspace_cards(loaded, local, cutoff)
    return {
        "cards": [card_json(card) for card in cards],
        "problems": [{"repository": p.repository, "message": p.message} for p in problems],
        "me": local.me,
        "columns": list(COLUMNS),
        "done_days": state.done_days,
        "workspace_id": workspace_id(state.workspace),
        "workspace": workspace_structure(loaded),
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
    }
