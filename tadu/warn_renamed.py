"""Tell the operator that a repository now goes by another name on GitHub."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.warn_operator import warn_operator

if TYPE_CHECKING:
    from tadu.access_store import AccessStore


def warn_renamed(store: AccessStore, name: str, now_named: str | None) -> None:
    """Warn once when GitHub answered `name` with a repository now named otherwise.

    A renamed or transferred repository still answers to its old name until someone
    creates a new repository with that name, so its remote should be updated.
    """
    if now_named is not None and now_named != name:
        warn_operator(
            store,
            f"{name} is now {now_named} on GitHub; update the remote of its workspace repository",
        )
