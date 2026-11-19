"""Follow every lead of an item back to where it was created."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.follow_lead import follow_lead
from tadu.history_order import history_order

if TYPE_CHECKING:
    from tadu.git_commit import GitCommit
    from tadu.history_event import HistoryEvent
    from tadu.history_lead import HistoryLead
    from tadu.history_source import HistorySource


def lead_events(source: HistorySource, leads: list[HistoryLead]) -> list[HistoryEvent]:
    """The changes behind the leads, in history order (see history_order), each commit once.

    A lead follows one line of descent; a merge that combined two branches' changes starts one
    per branch. Each lead is followed once.
    """
    followed: set[HistoryLead] = set()
    events: dict[str, tuple[GitCommit, HistoryEvent]] = {}
    newer: dict[str, set[str]] = {}
    while leads:
        lead = leads.pop(0)
        if lead in followed:
            continue
        followed.add(lead)
        event, more = follow_lead(source, lead)
        if event is not None and event.commit is not None:
            sha = event.commit.sha
            # keys: one event per commit; two branches reaching one commit found the same change
            events.setdefault(sha, (event.commit, event))
            newer.setdefault(sha, set()).update({lead.newer} if lead.newer else set())
        leads += more
    return history_order(events, newer)
