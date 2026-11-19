"""The JSON the board page renders."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from tadu.card_json import card_json
from tadu.columns import COLUMNS
from tadu.inbox_cards import inbox_cards
from tadu.load_local_config import load_local_config
from tadu.load_workspace import load_workspace
from tadu.view_summary import view_summary
from tadu.workspace_cards import workspace_cards
from tadu.workspace_id import workspace_id
from tadu.workspace_structure import workspace_structure

if TYPE_CHECKING:
    from collections.abc import Callable
    from datetime import date

    from tadu.board_state import BoardState
    from tadu.local_config import LocalConfig
    from tadu.payload_view import PayloadView
    from tadu.scan_problem import ScanProblem
    from tadu.workspace import Workspace


def board_payload(
    state: BoardState,
    today: date,
    narrow: Callable[[Workspace, LocalConfig], PayloadView] | None = None,
) -> dict[str, object]:
    """Re-scan the workspace; raise WorkspaceError when it no longer loads.

    Each card also says whether it is in the inbox of `me` (`tadu inbox`). A board that
    signs in with GitHub gives `narrow`, which cuts the workspace to what the signed-in
    person may see before anything is scanned, and names them as `user`.
    """
    loaded = load_workspace(state.workspace)
    local = load_local_config(state.workspace, loaded)
    access_problems: tuple[ScanProblem, ...] = ()
    user = None
    if narrow is not None:
        view = narrow(loaded, local)
        loaded, local, access_problems, user = view.workspace, view.local, view.problems, view.user
    cutoff = today - timedelta(days=state.done_days)
    cards, problems = workspace_cards(loaded, local, cutoff)
    mine = {id(card) for _, card in inbox_cards(cards, local.me, today)} if local.me else set()
    return {
        "cards": [card_json(card) | {"waiting_on_me": id(card) in mine} for card in cards],
        "problems": [
            {"repository": p.repository, "message": p.message}
            for p in (*access_problems, *problems)
        ],
        "me": local.me,
        "user": user,
        "columns": list(COLUMNS),
        "done_days": state.done_days,
        "workspace_id": workspace_id(state.workspace),
        "workspace": workspace_structure(loaded),
        "views": [view_summary(view) for view in loaded.views],
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
    }
