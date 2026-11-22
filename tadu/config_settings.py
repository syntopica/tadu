"""Which options a config file may set, per command, and where the user's file is.

A config file holds settings: where a command reads (`workspace`), how it prints
(`json`, `limit`), how a board is served. What one call acts on (an item, its text, a
filter) and `--write` stay on the command line; a filter set belongs in a saved view,
which `[list] view` can name. Who acts is not a setting either: `me` of the workspace's
local file and $TADU_ACTOR say it, so an agent's environment is never overruled.
"""

from __future__ import annotations

SCOPE = ("workspace",)
CONFIG_OPTIONS = {
    "doctor": (*SCOPE, "json"),
    "sync": ("file",),
    "init": ("file", "format"),
    "list": (*SCOPE, "done_days", "view", "json", "sort", "limit"),
    "show": (*SCOPE, "done_days", "json"),
    "ready": (*SCOPE, "json", "limit"),
    "next": (*SCOPE, "json"),
    "inbox": (*SCOPE, "json"),
    "urgent": (*SCOPE, "json", "days"),
    "prime": SCOPE,
    "similar": (*SCOPE, "limit"),
    "feed": (*SCOPE, "done_days"),
    "board": (
        *SCOPE,
        "host",
        "port",
        "done_days",
        "auth",
        "public_url",
        "sign_in_limit",
        "proxy_hops",
        "idle_timeout",
    ),
    "mcp": SCOPE,
}
# Where an option came from, when it was not a config file.
COMMAND_LINE = "the command line"
# Commands whose repository paths have no default `.`, so running in a repository does
# not make it their scope; a configured workspace stays theirs there.
NO_DEFAULT_PATH = frozenset({"doctor"})
# The table whose options apply to every command that takes them.
DEFAULTS_TABLE = "defaults"
# Names the user's config file instead of the default place.
CONFIG_VARIABLE = "TADU_CONFIG"
CONFIG_FILE_NAME = "config.toml"
