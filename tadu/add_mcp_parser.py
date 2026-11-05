"""Declare the mcp subcommand's arguments."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.add_scope_arguments import add_scope_arguments

if TYPE_CHECKING:
    import argparse


def add_mcp_parser(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add `mcp` to the subcommands."""
    mcp = commands.add_parser(
        "mcp", help="serve read-only list and show tools over MCP stdio (needs tadu[mcp])"
    )
    add_scope_arguments(mcp)
