"""One board card."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.backlog_item import BacklogItem
    from tadu.dependency import Dependency


@dataclass(frozen=True)
class Card:
    """An item with its repository, column, project context, links and resolved dependencies."""

    item: BacklogItem
    repository: str
    column: str
    project: str | None
    organizations: tuple[tuple[str, str], ...]
    editor_url: str | None
    remote_url: str | None
    dependencies: tuple[Dependency, ...] = ()
