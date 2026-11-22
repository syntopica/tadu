"""The JSON the board page renders."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

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
from tadu.writable_keys import writable_keys

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
    done_days: int,
    today: date,
    narrow: Callable[[Workspace, LocalConfig], PayloadView] | None = None,
) -> dict[str, object]:
    """Re-scan the workspace, closed items `done_days` back; WorkspaceError when it does not load.

    Each card also says whether it is in the inbox of `me` (`tadu inbox`), and which cards
    name it in their relations (`linked_from`, as `tadu show` lists them). `allow` is what the
    page may do (see board_call), `writable` the checked-out repositories whose items it may
    change (both --allow and the repository's access allow it), `formats` the backlog format of each
    checked-out repository, and `tools` the input schema of each call it may make;
    `today` is the server's day, and `sections` titles the sections of `urgent` and `inbox`.

    A board that signs in with GitHub gives `narrow`, which cuts the workspace to what the
    signed-in person may see before anything is scanned, and names them as `user`; so every
    list above, `writable` and `formats` included, covers only those repositories.
    """
    loaded = load_workspace(state.workspace)
    local = load_local_config(state.workspace, loaded)
    access_problems: tuple[ScanProblem, ...] = ()
    user = None
    if narrow is not None:
        view = narrow(loaded, local)
        loaded, local, access_problems, user = view.workspace, view.local, view.problems, view.user
    cutoff = today - timedelta(days=done_days)
    cards, problems = workspace_cards(loaded, local, cutoff)
    unread = {problem.repository for problem in problems}
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
        "problems": [
            {"repository": p.repository, "message": p.message}
            for p in (*access_problems, *problems)
        ],
        "me": local.me,
        "user": user,
        "columns": list(COLUMNS),
        "sections": SECTION_TITLES,
        "done_days": done_days,
        "allow": state.allow,
        # keys: load_workspace rejects a repository key used twice. A repository that could not
        # be read has none: one in a newer format would raise here.
        "formats": {
            entry.key: backlog_format(str(local.paths[entry.key] / entry.backlog))
            for entry in loaded.repositories
            if entry.key in local.paths and entry.key not in unread
        },
        "writable": writable_keys(state.allow, loaded, local),
        "tools": {name: tool["inputSchema"] for name, tool in operation_tools(state.allow).items()},
        "today": today.isoformat(),
        "workspace_id": workspace_id(state.workspace),
        "workspace": workspace_structure(loaded),
        "views": [view_summary(view) for view in loaded.views],
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
    }
