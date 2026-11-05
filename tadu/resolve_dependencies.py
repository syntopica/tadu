"""Attach the resolved `Depends on:` targets to each card."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from tadu.dependency import Dependency
from tadu.stable_card_index import stable_card_index

if TYPE_CHECKING:
    from tadu.card import Card


def resolve_dependencies(cards: tuple[Card, ...]) -> tuple[Card, ...]:
    """The cards with their dependencies looked up by ID among the same cards."""
    index = stable_card_index(cards)
    resolved: list[Card] = []
    for card in cards:
        dependencies: list[Dependency] = []
        for target in card.item.depends_on:
            found = index.get(target)
            dependencies.append(
                Dependency(target, None, None, None)
                if found is None
                else Dependency(target, found.repository, found.item.state, found.column)
            )
        resolved.append(replace(card, dependencies=tuple(dependencies)))
    return tuple(resolved)
