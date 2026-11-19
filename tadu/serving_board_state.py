"""The state of a board server once its port is known."""

from __future__ import annotations

import secrets
from pathlib import Path
from typing import TYPE_CHECKING

from tadu.allowed_hosts import allowed_hosts
from tadu.board_state import BoardState

if TYPE_CHECKING:
    import argparse
    from collections.abc import Callable

    from tadu.github_sign_in import GithubSignIn


def serving_board_state(
    args: argparse.Namespace,
    port: int,
    main: Callable[[list[str]], int],
    github: GithubSignIn | None = None,
) -> BoardState:
    """A fresh token and the Host values of the bound address, with what the page may do.

    With GitHub sign-in, the host of its public URL is accepted too.
    """
    hosts = allowed_hosts(args.host, port)
    if github is not None:
        hosts |= {github.public_host}
    token = secrets.token_urlsafe(32)
    return BoardState(Path(args.workspace), args.done_days, token, hosts, args.allow, main, github)
