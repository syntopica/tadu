"""What one board server needs to answer a request."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from tadu.github_sign_in import GithubSignIn


@dataclass(frozen=True)
class BoardState:
    """What the board serves, and what it lets the page do.

    The workspace, the Done window, the per-run token, the accepted Host values, the access
    level the board was started with, and the tadu command line its tool calls run. With
    `github`, people sign in with GitHub instead of presenting the token.
    """

    workspace: Path
    done_days: int
    token: str
    allowed_hosts: frozenset[str]
    allow: str
    main: Callable[[list[str]], int]
    github: GithubSignIn | None = None
