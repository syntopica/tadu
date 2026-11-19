"""The checkout a card was read from."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.root_labels import root_labels

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.local_config import LocalConfig


def card_root(paths: tuple[str, ...], local: LocalConfig | None, repository: str) -> Path:
    """The root of the card's repository: from the workspace's local paths, else the roots given.

    `paths`, `local` and `repository` are those `load_cards` read the card with.
    """
    roots = local.paths if local is not None else root_labels(paths or (".",))
    return roots[repository]
