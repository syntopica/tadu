"""The JSON the board page renders."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from tadu.card_json import card_json
from tadu.columns import COLUMNS
from tadu.load_cards import load_cards

if TYPE_CHECKING:
    from datetime import date

    from tadu.board_state import BoardState


def board_payload(state: BoardState, today: date) -> dict[str, object]:
    """Re-scan the workspace; raise WorkspaceError when it no longer loads."""
    cards, problems, local = load_cards((), str(state.workspace), state.done_days, today)
    return {
        "cards": [card_json(card) for card in cards],
        "problems": [{"repository": p.repository, "message": p.message} for p in problems],
        "me": local.me if local else None,
        "columns": list(COLUMNS),
        "done_days": state.done_days,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
    }
