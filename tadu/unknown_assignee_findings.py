"""W001 findings for assignees who are not people of the workspace."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.finding import Finding

if TYPE_CHECKING:
    from tadu.card import Card
    from tadu.local_config import LocalConfig
    from tadu.workspace import Workspace


def unknown_assignee_findings(
    workspace: Workspace, local: LocalConfig, cards: tuple[Card, ...]
) -> tuple[Finding, ...]:
    """One warning per card and unknown assignee."""
    known = {person.id for person in workspace.people}
    return tuple(
        Finding(
            "W001",
            "warning",
            str(local.paths[card.repository] / card.item.path),
            card.item.line,
            f"assignee {assignee} is not a person in the workspace",
        )
        for card in cards
        for assignee in card.item.fields.assignees
        if assignee not in known
    )
