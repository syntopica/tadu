"""Which function runs each command, by the name of the module that holds it.

cli imports a command's module only when that command runs, so a call of `tadu list`
does not load the board's server or the MCP server first.
"""

from __future__ import annotations

# Commands run as function(args, today).
DATED_COMMANDS = {
    "add": "dispatch_add",
    "set": "run_set",
    "claim": "run_claim",
    "archive": "run_archive",
    "list": "run_list",
    "show": "run_show",
    "next": "run_next",
    "inbox": "run_inbox",
    "urgent": "run_urgent",
    "ready": "run_ready",
    "similar": "run_similar",
    "feed": "run_feed",
    "doctor": "doctor_command",
}
# Commands run as function(args).
PLAIN_COMMANDS = {
    "close": "close_command",
    "mark": "mark_command",
    "fmt": "run_fmt",
    "migrate": "run_migrate",
    "board": "run_board",
}
