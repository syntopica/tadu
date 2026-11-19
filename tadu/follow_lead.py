"""Follow one lead to the commit that gave the item its text."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.first_change import first_change
from tadu.holds_item_text import holds_item_text
from tadu.lead_at import lead_at
from tadu.pickaxe_commit import pickaxe_commit

# Linux takes at most 128 KiB in one argument; a longer item is read commit by commit.
MAX_SEARCH_BYTES = 100_000

if TYPE_CHECKING:
    from tadu.history_event import HistoryEvent
    from tadu.history_lead import HistoryLead
    from tadu.history_source import HistorySource


def follow_lead(
    source: HistorySource, lead: HistoryLead
) -> tuple[HistoryEvent | None, tuple[HistoryLead, ...]]:
    """The change found behind the lead, if any, and the leads to follow from there.

    `git log -S` names the commit, searching only the file the text is in: the commit that put
    it there changed that file, even when it moved the item from the other one. When that
    commit does not hold the item's text, the change was one the search cannot see, and the
    commits are read one by one instead, as they are for an item too long to search for.
    """
    searchable = len(lead.text.encode()) <= MAX_SEARCH_BYTES
    spec = (source.pathspec(lead.path),)
    commit = pickaxe_commit(source.root, lead.text, lead.tips, spec) if searchable else None
    if searchable and commit is None:
        return None, ()
    if commit is None or not holds_item_text(
        source.blobs.read(source.name(commit.sha, lead.path)), lead.text
    ):
        commit = first_change(source, lead)
        if commit is None:
            return None, ()
    return lead_at(source, commit, lead)
