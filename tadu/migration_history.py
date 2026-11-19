"""The history a task had as a Markdown item, before `tadu migrate` made it a task file."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from tadu.history_lead import HistoryLead
from tadu.lead_events import lead_events
from tadu.markdown_files import markdown_files
from tadu.migrated_item import migrated_item

if TYPE_CHECKING:
    from tadu.history_event import HistoryEvent
    from tadu.history_source import HistorySource


def migration_history(
    source: HistorySource, first: HistoryEvent, backlog: str
) -> list[HistoryEvent]:
    """`first`, a task's oldest change, then the history of the Markdown item it came from.

    When `first` created the task in a commit whose first parent held that item in the
    backlog's Markdown files, the creation was `tadu migrate`: it becomes a change from the
    item to the task, and the item's own history follows, newest first. Otherwise `first`
    alone.
    """
    commit = first.commit
    if first.before is not None or commit is None or not commit.parents:
        return [first]
    parent = commit.parents[0]
    old = migrated_item(source, parent, backlog, first.after.key)
    if old is None:
        return [first]
    markdown = replace(source, paths=markdown_files(old.path))
    older = lead_events(markdown, [HistoryLead(old.path, old.text, (parent,), commit.sha)])
    return [replace(first, before=old), *older]
