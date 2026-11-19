"""Which repositories a command reads or changes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Scope:
    """Repository roots (default `.`) or a workspace directory, and maybe one repository of them.

    `repository` is a workspace key or the label a root's items carry; a reading command reads
    only it, and a writing command changes it.
    """

    paths: tuple[str, ...] = ()
    workspace: str | None = None
    repository: str | None = None
