"""Decide whether a card satisfies a filter."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.card import Card
    from tadu.card_filter import CardFilter


def card_matches(card: Card, card_filter: CardFilter) -> bool:
    """Return True when the card meets every criterion set on the filter."""
    fields = card.item.fields
    checks = (
        card_filter.project in (None, card.project),
        card_filter.column in (None, card.column),
        card_filter.priority in (None, fields.priority),
        card_filter.assignee is None or card_filter.assignee in fields.assignees,
        card_filter.label is None or card_filter.label in fields.labels,
        card_filter.due_before is None
        or (fields.due is not None and fields.due < card_filter.due_before),
        (card_filter.role is None and card_filter.org is None)
        or any(
            card_filter.role in (None, role) and card_filter.org in (None, org)
            for role, org in card.organizations
        ),
        card.column != "cancelled"
        or card_filter.include_cancelled
        or card_filter.column == "cancelled",
    )
    return all(checks)
