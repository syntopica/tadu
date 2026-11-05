"""Declare the feed subcommand's arguments."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.add_scope_arguments import add_scope_arguments

if TYPE_CHECKING:
    import argparse


def add_feed_parser(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add `feed` to the subcommands."""
    feed = commands.add_parser("feed", help="print recently closed items as JSON, newest first")
    add_scope_arguments(feed)
