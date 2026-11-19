"""Everything a board signing in with GitHub needs before it listens."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from tadu.board_memory import board_memory
from tadu.github_client import github_client
from tadu.github_sign_in import GithubSignIn
from tadu.sign_in_limiter import SignInLimiter
from tadu.sign_in_settings import IDLE_TIMEOUT_SECONDS

if TYPE_CHECKING:
    import argparse
    from collections.abc import Callable


def prepare_team_board(args: argparse.Namespace) -> Callable[[int], GithubSignIn]:
    """How to make the sign-in once the port is known.

    The app's client comes from the environment, the ids and sessions from beside the
    workspace; the public URL defaults to http://HOST:PORT.

    Raise ValueError when the client is missing or the ids cannot be read.
    """
    client_id, secret = github_client(os.environ)
    pins, sessions = board_memory(args.workspace, args.idle_timeout or IDLE_TIMEOUT_SECONDS)

    def sign_in(port: int) -> GithubSignIn:
        public_url = args.public_url or f"http://{args.host}:{port}"
        return GithubSignIn(
            client_id,
            secret,
            public_url,
            sessions=sessions,
            pins=pins,
            limiter=SignInLimiter(args.sign_in_limit),
            proxy_hops=args.proxy_hops or 0,
        )

    return sign_in
