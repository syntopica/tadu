"""The board paths that answer from the server's state and so require the token."""

from __future__ import annotations

# The cards: backlog data.
BOARD_DATA_PATH = "/api/cards"
# Whether the page may still show what it shows: the board is up, and the token (or,
# with GitHub sign-in, the session) still holds. Light: it reads no backlog and asks
# GitHub nothing.
BOARD_CHECK_PATH = "/api/session"
