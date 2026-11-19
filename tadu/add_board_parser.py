"""Declare the board subcommand's arguments."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.idle_timeout import idle_timeout
from tadu.non_negative_int import non_negative_int
from tadu.public_board_url import public_board_url
from tadu.sign_in_limit import sign_in_limit
from tadu.sign_in_settings import SIGN_IN_LIMIT

if TYPE_CHECKING:
    import argparse


def add_board_parser(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add `board` to the subcommands."""
    board = commands.add_parser("board", help="serve a read-only kanban page for a workspace")
    board.add_argument(
        "--workspace",
        required=True,
        help="directory holding tadu-workspace.toml (required, here or in a config file)",
    )
    board.add_argument("--host", default="127.0.0.1", help="address to bind (default: 127.0.0.1)")
    board.add_argument(
        "--port",
        type=non_negative_int,
        default=None,
        help="port to bind; 0 for any free port (default: one derived from the workspace path, "
        "or any free port when that one is busy)",
    )
    board.add_argument(
        "--done-days",
        type=non_negative_int,
        default=14,
        help="show done and cancelled items this many days back (default: 14)",
    )
    board.add_argument(
        "--auth",
        choices=("token", "github"),
        default="token",
        help="token: the printed URL opens the board; github: people sign in with GitHub and "
        "see only the repositories they can read there, with the app's client ID and secret "
        "in TADU_GITHUB_CLIENT_ID and TADU_GITHUB_CLIENT_SECRET (default: token)",
    )
    board.add_argument(
        "--public-url",
        type=public_board_url,
        default=None,
        help="with --auth github, the address people open, such as https://tadu.example.com "
        "or https://example.com/tadu, whose /auth/callback is the app's callback URL "
        "(default: http://HOST:PORT)",
    )
    board.add_argument(
        "--sign-in-limit",
        type=sign_in_limit,
        default=None,
        metavar="LIMITS",
        help="with --auth github, how often one address may start a sign-in, and come back "
        "from GitHub, each: like 10/minute or 10/minute;100/hour, or off "
        f"(default: {SIGN_IN_LIMIT})",
    )
    board.add_argument(
        "--idle-timeout",
        type=idle_timeout,
        default=None,
        metavar="DURATION",
        help="with --auth github, sign a person out after this long without activity, "
        "such as 14d, 8h or 30m, at least 10m; an open page warns 5 minutes before "
        "(default: 14d)",
    )
    board.add_argument(
        "--proxy-hops",
        type=non_negative_int,
        default=None,
        metavar="N",
        help="with --auth github, how many proxies in front of the board to trust for the "
        "client's address in X-Forwarded-For (default: 0, the header is ignored)",
    )
