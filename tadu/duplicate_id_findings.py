"""W002 findings for IDs used in more than one repository."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.finding import Finding

if TYPE_CHECKING:
    from tadu.card import Card
    from tadu.local_config import LocalConfig


def duplicate_id_findings(local: LocalConfig, cards: tuple[Card, ...]) -> tuple[Finding, ...]:
    """Report each later occurrence of a valid ID first seen in another repository."""
    first: dict[str, Card] = {}
    findings: list[Finding] = []
    for card in cards:
        item_id = card.item.fields.id
        if not card.item.stable or item_id is None:
            continue
        earlier = first.setdefault(item_id, card)
        if earlier.repository == card.repository:
            continue
        where = f"{earlier.repository}:{earlier.item.path}:{earlier.item.line}"
        path = str(local.paths[card.repository] / card.item.path)
        message = f"ID {item_id} is also used in {where}"
        findings.append(Finding("W002", "warning", path, card.item.line, message))
    return tuple(findings)
