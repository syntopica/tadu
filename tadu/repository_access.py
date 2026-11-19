"""What a signed-in person may see of the workspace's repositories."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RepositoryAccess:
    """What a signed-in person may see of the workspace's repositories.

    The readable repository keys; the status of a recent check that could not tell;
    whether a readable repository is hidden because the board could not confirm it is
    the GitHub repository it was.
    """

    readable: frozenset[str]
    failed: int | None = None
    unconfirmed: bool = False
