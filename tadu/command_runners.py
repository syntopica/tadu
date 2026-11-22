"""Which function runs each command, by the name of the module that holds it.

cli imports a command's module only when that command runs, so a call of `tadu list`
does not load the board's server or the MCP server first.
"""

from __future__ import annotations

# Commands run as function(args, today).
DATED_COMMANDS = {
    "add": "dispatch_add",
    "set": "run_set",
    "claim": "claim_command",
    "close": "close_command",
    "mark": "mark_command",
    "archive": "run_archive",
    "list": "run_list",
    "show": "run_show",
    "changes": "run_changes",
    "next": "run_next",
    "inbox": "run_inbox",
    "urgent": "run_urgent",
    "prime": "run_prime",
    "ready": "run_ready",
    "similar": "run_similar",
    "feed": "run_feed",
    "doctor": "doctor_command",
}
# Commands run as function(args).
PLAIN_COMMANDS = {
    "fmt": "run_fmt",
    "migrate": "migrate_command",
}
# Servers run as function(args, main): they call tadu's own command line for each request.
SERVER_COMMANDS = {
    "board": "run_board",
    "mcp": "run_mcp",
}
# Commands that change a backlog hold its lock while they run.
LOCKED_COMMANDS = frozenset({"set", "archive", "fmt", "migrate"})
