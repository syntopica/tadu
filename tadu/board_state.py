"""What one board server needs to answer a request."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.github_sign_in import GithubSignIn


@dataclass(frozen=True)
class BoardState:
    """The workspace directory, the Done window, the per-run token and the accepted Host values.

    With `github`, people sign in with GitHub instead of presenting the token.
    """

    workspace: Path
    done_days: int
    token: str
    allowed_hosts: frozenset[str]
    github: GithubSignIn | None = None
