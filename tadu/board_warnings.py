"""What a board server warns about when it starts."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.loopback_hosts import LOOPBACK_HOSTS
from tadu.team_board_warnings import team_board_warnings
from tadu.unique_in_order import unique_in_order

if TYPE_CHECKING:
    import argparse

    from tadu.board_state import BoardState


def board_warnings(args: argparse.Namespace, state: BoardState, port: int) -> list[str]:
    """A bind address other than loopback, and what GitHub sign-in cannot protect.

    With GitHub sign-in, team_board_warnings' too.
    """
    warnings = []
    names = [f"{args.host}:{port}"]
    if state.github is not None:
        names.append(state.github.public_host)
    if args.host not in LOOPBACK_HOSTS:
        shown = " or ".join(unique_in_order(names))
        warnings.append(
            f"listening on {args.host}; only requests whose Host header is {shown} are served"
            + (
                ""
                if args.allow == "read" or state.github
                else f", and with the token they may {args.allow}"
            )
        )
    if state.github is not None:
        warnings += team_board_warnings(args, state.github, state.workspace)
    return warnings
