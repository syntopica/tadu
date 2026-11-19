"""The history of one item of a Markdown backlog (format v1)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.blob_reader import BlobReader
from tadu.history_event import HistoryEvent
from tadu.history_lead import HistoryLead
from tadu.history_source import HistorySource
from tadu.item_step import item_step
from tadu.lead_events import lead_events
from tadu.markdown_files import markdown_files
from tadu.working_versions import working_versions

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.backlog_item import BacklogItem


def markdown_history(
    root: Path, prefix: str, item: BacklogItem, repository: str
) -> tuple[HistoryEvent, ...]:
    """Each change to the item, newest first (uncommitted ones on top), back to its creation.

    From the item's text at HEAD, `git log -S` finds the commit that gave it that text; the
    text before it leads to the next one (see lead_events). The item is followed through
    TODO.md and TODO_LOG.md by its text, so a title edit, closing into the log or an `ID:`
    added later does not lose it (see previous_item).
    """
    with BlobReader(root) as blobs:
        source = HistorySource(root, prefix, markdown_files(item.path), repository, blobs)
        start = frozenset({(item.path, item.text)})
        step, texts = item_step(working_versions(source), start, repository)
        leads = [HistoryLead(path, text, ("HEAD",)) for path, text in sorted(texts)]
        events = lead_events(source, leads)
    return tuple([HistoryEvent(None, *step)] if step else []) + tuple(events)
