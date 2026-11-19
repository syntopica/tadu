"""One backlog file at one change."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FileVersions:
    """The file's path in the checkout, its text in each parent and after the change.

    Texts are lines joined with line feeds; an absent file is empty text.
    """

    path: str
    before: tuple[str, ...]
    after: str
