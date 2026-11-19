"""What one commit did to the item a lead follows."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.history_event import HistoryEvent
from tadu.history_lead import HistoryLead
from tadu.holds_item_text import holds_item_text
from tadu.markdown_items import markdown_items
from tadu.previous_item import previous_item
from tadu.versions_at import versions_at

if TYPE_CHECKING:
    from tadu.git_commit import GitCommit
    from tadu.history_source import HistorySource


def lead_at(
    source: HistorySource, commit: GitCommit, lead: HistoryLead
) -> tuple[HistoryEvent | None, tuple[HistoryLead, ...]]:
    """The change the commit made to the item, if any, and the leads to follow further back.

    A parent that already held the text carries the lead on, without a change: a merge that
    took one branch's version, or the text also present elsewhere. Otherwise the commit gave
    the item its text: one lead per parent where it had another, none where it was created.
    The item is parsed from its own text, which the caller found whole in the commit.
    """
    held = tuple(
        sha
        for sha in commit.parents
        if holds_item_text(source.blobs.read(source.name(sha, lead.path)), lead.text)
    )
    if held:
        return None, (HistoryLead(lead.path, lead.text, held, lead.newer),)
    new = markdown_items(lead.text, source.repository, lead.path)
    if not new:
        return None, ()
    versions = versions_at(source, commit)
    befores = [
        previous_item(versions, parent, new[0], source.repository)
        for parent in range(max(len(commit.parents), 1))
    ]
    leads = tuple(
        HistoryLead(before.path, before.text, (sha,), commit.sha)
        for sha, before in zip(commit.parents, befores, strict=False)
        if before is not None
    )
    earlier = [before for before in befores if before is not None]
    return HistoryEvent(commit, earlier[0] if earlier else None, new[0]), leads
