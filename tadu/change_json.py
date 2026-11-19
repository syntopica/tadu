"""JSON-ready form of one backlog change."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from tadu.change_entry import ChangeEntry
from tadu.history_event import HistoryEvent
from tadu.history_json import history_json

if TYPE_CHECKING:
    from tadu.backlog_item import BacklogItem
    from tadu.change_source import ChangeSource
    from tadu.git_commit import GitCommit


def change_json(
    source: ChangeSource,
    commit: GitCommit,
    pair: tuple[BacklogItem | None, BacklogItem | None],
    event: str,
) -> ChangeEntry:
    """The change's history entry (see history_json) with its item's context and the event.

    The context is the repository, project, key and title. A removed item's entry is about the item as it was: its file became none, and it has no
    text after.
    """
    before, after = pair
    item = cast("BacklogItem", after or before)  # every pair has the item on one side
    if after is None:
        entry = history_json(HistoryEvent(commit, None, item))
        entry |= {
            "created": False,
            "changes": [{"field": "file", "before": item.path, "after": None}],
            "lines": [],
            "before_text": item.text,
            "after_text": "",
        }
    else:
        entry = history_json(HistoryEvent(commit, before, after))
    return ChangeEntry(
        **entry,
        repository=source.repository,
        project=source.project,
        key=item.fields.id,
        title=item.title,
        event=event,
    )
