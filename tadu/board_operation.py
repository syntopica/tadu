"""The board operation."""

from __future__ import annotations

from tadu.access_levels import ACCESS_LEVELS
from tadu.board_sign_in_params import BOARD_SIGN_IN_PARAMS
from tadu.operation import Operation
from tadu.param import Param
from tadu.shared_params import DONE_DAYS
from tadu.workspace_help import WORKSPACE_HELP

BOARD_OPERATION = Operation(
    "board",
    "serve a kanban page for a workspace; read-only unless --allow says more",
    (
        Param(
            "workspace",
            "text",
            f"{WORKSPACE_HELP} (required, here or in a config file)",
            required=True,
            metavar="DIR",
        ),
        Param("host", "text", "address to bind (default: 127.0.0.1)", default="127.0.0.1"),
        Param(
            "port",
            "count",
            "port to bind; 0 for any free port (default: one derived from the workspace "
            "path, or any free port when that one is busy)",
        ),
        DONE_DAYS,
        Param(
            "allow",
            "choice",
            "what the page may do: read (default), write items, or admin (also archive, "
            "fmt, migrate, sync and init)",
            ACCESS_LEVELS,
            default="read",
        ),
        Param(
            "auth",
            "choice",
            "token: the printed URL opens the board; github: people sign in with GitHub and "
            "see only the repositories they can read there, with the app's client ID and "
            "secret in TADU_GITHUB_CLIENT_ID and TADU_GITHUB_CLIENT_SECRET (default: token)",
            ("token", "github"),
            default="token",
        ),
        *BOARD_SIGN_IN_PARAMS,
    ),
    access="local",
    target="none",
)
