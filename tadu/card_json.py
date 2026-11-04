"""JSON-ready form of a card."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.iso_date import iso_date

if TYPE_CHECKING:
    from tadu.card import Card


def card_json(card: Card) -> dict[str, object]:
    """The card as plain dicts, lists and strings; problem lines are 1-based."""
    item, fields = card.item, card.item.fields
    return {
        "key": item.key,
        "stable": item.stable,
        "repository": card.repository,
        "path": item.path,
        "line": item.line,
        "end_line": item.end_line,
        "state": item.state,
        "column": card.column,
        "title": item.title,
        "text": item.text,
        "day": iso_date(item.day),
        "priority": fields.priority,
        "assignees": list(fields.assignees),
        "due": iso_date(fields.due),
        "labels": list(fields.labels),
        "queue": fields.queue,
        "estimate": fields.estimate,
        "project": card.project,
        "organizations": [{"role": r, "org": o} for r, o in card.organizations],
        "problems": [{"line": p.line + 1, "message": p.message} for p in item.problems],
        "editor_url": card.editor_url,
        "remote_url": card.remote_url,
    }
