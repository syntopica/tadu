"""Build the command-line parser: every subcommand and its arguments."""

from __future__ import annotations

import argparse
from importlib.metadata import version

from tadu.add_add_parser import add_add_parser
from tadu.add_attention_parsers import add_attention_parsers
from tadu.add_board_parser import add_board_parser
from tadu.add_claim_parser import add_claim_parser
from tadu.add_close_parser import add_close_parser
from tadu.add_doctor_parser import add_doctor_parser
from tadu.add_feed_parser import add_feed_parser
from tadu.add_init_parser import add_init_parser
from tadu.add_list_parser import add_list_parser
from tadu.add_mark_parser import add_mark_parser
from tadu.add_mcp_parser import add_mcp_parser
from tadu.add_ready_parser import add_ready_parser
from tadu.add_set_parser import add_set_parser
from tadu.add_show_parser import add_show_parser
from tadu.add_similar_parser import add_similar_parser
from tadu.add_sync_parser import add_sync_parser
from tadu.add_task_command_parsers import add_task_command_parsers


def build_parser(description: str | None) -> argparse.ArgumentParser:
    """The `tadu` parser with all subcommands, in the order `tadu --help` lists them."""
    parser = argparse.ArgumentParser(prog="tadu", description=description)
    parser.add_argument("--version", action="version", version=f"tadu {version('tadu')}")
    commands = parser.add_subparsers(dest="command", required=True)
    add_doctor_parser(commands)
    add_sync_parser(commands)
    add_init_parser(commands)
    add_list_parser(commands)
    add_show_parser(commands)
    add_ready_parser(commands)
    add_attention_parsers(commands)
    add_similar_parser(commands)
    add_feed_parser(commands)
    add_board_parser(commands)
    add_close_parser(commands)
    add_add_parser(commands)
    add_mark_parser(commands)
    add_mcp_parser(commands)
    add_set_parser(commands)
    add_claim_parser(commands)
    add_task_command_parsers(commands)
    hook = commands.add_parser("hook", help="agent hooks that run doctor after a backlog change")
    hook.add_argument("agent", choices=["claude"], help="claude: a Claude Code PostToolUse hook")
    return parser
