"""The operations that only run on this machine: the servers and the hook."""

from __future__ import annotations

from tadu.access_levels import ACCESS_LEVELS
from tadu.idle_timeout import idle_timeout
from tadu.non_negative_int import non_negative_int
from tadu.operation import Operation
from tadu.param import Param
from tadu.public_board_url import public_board_url
from tadu.shared_params import DONE_DAYS
from tadu.sign_in_limit import sign_in_limit
from tadu.sign_in_settings import SIGN_IN_LIMIT

WORKSPACE = "directory holding tadu-workspace.toml"

LOCAL_OPERATIONS = (
    Operation(
        "board",
        "serve a kanban page for a workspace; read-only unless --allow says more",
        (
            Param(
                "workspace",
                "text",
                f"{WORKSPACE} (required, here or in a config file)",
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
            Param(
                "public_url",
                "text",
                "with --auth github, the address people open, such as https://tadu.example.com "
                "or https://example.com/tadu, whose /auth/callback is the app's callback URL "
                "(default: http://HOST:PORT)",
                parse=public_board_url,
            ),
            Param(
                "sign_in_limit",
                "text",
                "with --auth github, how often one address may start a sign-in, and come back "
                "from GitHub, each: like 10/minute or 10/minute;100/hour, or off "
                f"(default: {SIGN_IN_LIMIT})",
                metavar="LIMITS",
                parse=sign_in_limit,
            ),
            Param(
                "idle_timeout",
                "text",
                "with --auth github, sign a person out after this long without activity, "
                "such as 14d, 8h or 30m, at least 10m; an open page warns 5 minutes before "
                "(default: 14d)",
                metavar="DURATION",
                parse=idle_timeout,
            ),
            Param(
                "proxy_hops",
                "count",
                "with --auth github, how many proxies in front of the board to trust for the "
                "client's address in X-Forwarded-For (default: 0, the header is ignored)",
                metavar="N",
                parse=non_negative_int,
            ),
        ),
        access="local",
        target="none",
    ),
    Operation(
        "mcp",
        "serve the backlog as MCP tools over stdio; read-only unless --allow says more",
        (
            Param("paths", "list", "repository roots (default: .)", positional=True),
            Param("workspace", "text", WORKSPACE, metavar="DIR"),
            Param(
                "allow",
                "choice",
                "what the tools may do: read (default), write items, or admin (also archive, "
                "fmt, migrate, sync and init)",
                ACCESS_LEVELS,
                default="read",
            ),
        ),
        access="local",
        target="none",
    ),
    Operation(
        "hook",
        "agent hooks that run doctor after a backlog change",
        (
            Param(
                "agent",
                "choice",
                "claude: a Claude Code PostToolUse hook",
                ("claude",),
                required=True,
                positional=True,
            ),
        ),
        access="local",
        target="none",
    ),
)
