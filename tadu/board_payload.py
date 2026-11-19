"""The JSON the board page renders."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from tadu.access_allows import access_allows
from tadu.backlog_format import backlog_format
from tadu.card_json import card_json
from tadu.columns import COLUMNS
from tadu.inbox_cards import inbox_cards
from tadu.load_local_config import load_local_config
from tadu.load_workspace import load_workspace
from tadu.operation_tools import operation_tools
from tadu.reverse_relation_index import reverse_relation_index
from tadu.section_titles import SECTION_TITLES
from tadu.view_summary import view_summary
from tadu.workspace_cards import workspace_cards
from tadu.workspace_id import workspace_id
from tadu.workspace_structure import workspace_structure

if TYPE_CHECKING:
    from datetime import date

    from tadu.board_state import BoardState


def board_payload(state: BoardState, done_days: int, today: date) -> dict[str, object]:
    """Re-scan the workspace, closed items `done_days` back; WorkspaceError when it does not load.

    Each card also says whether it is in the inbox of `me` (`tadu inbox`), and which cards
    name it in their relations (`linked_from`, as `tadu show` lists them). `allow` is what the
    page may do (see board_call), `writable` the checked-out repositories whose items it may
    change (both --allow and the repository's access allow it), `formats` the backlog format of each
    checked-out repository, and `tools` the input schema of each call it may make;
    `today` is the server's day, and `sections` titles the sections of `urgent` and `inbox`.
    """
    loaded = load_workspace(state.workspace)
    local = load_local_config(state.workspace, loaded)
    cutoff = today - timedelta(days=done_days)
    cards, problems = workspace_cards(loaded, local, cutoff)
    mine = {id(card) for _, card in inbox_cards(cards, local.me, today)} if local.me else set()
    pointing = reverse_relation_index(cards)
    return {
        "cards": [
            card_json(card)
            | {
                "waiting_on_me": id(card) in mine,
                "linked_from": [
                    {"kind": name, "key": other.item.key}
                    for name, other in pointing.get(card.item.key, [])
                ],
            }
            for card in cards
        ],
        "problems": [{"repository": p.repository, "message": p.message} for p in problems],
        "me": local.me,
        "columns": list(COLUMNS),
        "sections": SECTION_TITLES,
        "done_days": done_days,
        "allow": state.allow,
        # keys: load_workspace rejects a repository key used twice.
        "formats": {
            entry.key: backlog_format(str(local.paths[entry.key] / entry.backlog))
            for entry in loaded.repositories
            if entry.key in local.paths
        },
        "writable": [
            entry.key
            for entry in loaded.repositories
            if access_allows(state.allow, "write")
            and access_allows(entry.access, "write")
            and entry.key in local.paths
        ],
        "tools": {name: tool["inputSchema"] for name, tool in operation_tools(state.allow).items()},
        "today": today.isoformat(),
        "workspace_id": workspace_id(state.workspace),
        "workspace": workspace_structure(loaded),
        "views": [view_summary(view) for view in loaded.views],
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
    }
