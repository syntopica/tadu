"""Cards for the items of one repository."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.card import Card
from tadu.editor_line_url import editor_line_url
from tadu.forge_line_url import forge_line_url
from tadu.item_column import item_column

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.backlog_item import BacklogItem
    from tadu.local_config import LocalConfig
    from tadu.project_entry import ProjectEntry
    from tadu.repository_entry import RepositoryEntry


def build_cards(  # noqa: PLR0913, PLR0917
    items: tuple[BacklogItem, ...],
    repository: str,
    root: Path,
    entry: RepositoryEntry | None,
    project: ProjectEntry | None,
    local: LocalConfig | None,
) -> tuple[Card, ...]:
    """One card per item, in order, with project context and links."""
    template = local.editor_url if local else None
    remote = entry.remote if entry else None
    return tuple(
        Card(
            item=item,
            repository=repository,
            column=item_column(item.state, item.fields.queue),
            project=project.key if project else None,
            organizations=project.roles if project else (),
            editor_url=editor_line_url(template, root / item.path, item.line),
            remote_url=forge_line_url(remote, item.path, item.line),
        )
        for item in items
    )
