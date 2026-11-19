"""Bind the board handler to one server's state."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.board_handler import BoardHandler

if TYPE_CHECKING:
    from http.server import BaseHTTPRequestHandler

    from tadu.board_state import BoardState


def make_board_handler(state: BoardState) -> type[BaseHTTPRequestHandler]:
    """A BoardHandler subclass that answers for this state.

    With `state.github`, a TeamBoardHandler that signs people in with GitHub.
    """
    if state.github is None:
        return type("BoundBoardHandler", (BoardHandler,), {"state": state})
    from tadu.team_board_handler import TeamBoardHandler  # noqa: PLC0415 - loaded only when signing in with GitHub

    return type(
        "BoundTeamBoardHandler", (TeamBoardHandler,), {"state": state, "sign_in": state.github}
    )
