"""Bind the board handler to one server's state."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.board_handler import BoardHandler

if TYPE_CHECKING:
    from http.server import BaseHTTPRequestHandler

    from tadu.board_state import BoardState


def make_board_handler(state: BoardState) -> type[BaseHTTPRequestHandler]:
    """A BoardHandler subclass that answers for this state."""
    return type("BoundBoardHandler", (BoardHandler,), {"state": state})
