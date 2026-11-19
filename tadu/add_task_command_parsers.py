"""Declare the archive, fmt and migrate subcommands."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse

COMMANDS = (
    (
        "archive",
        "move old closed tasks to todo/archive/ as todo/tadu.json's policy says (format v2)",
    ),
    ("fmt", "rewrite task files that are not in canonical form (format v2)"),
    ("migrate", "turn a TODO.md / TODO_LOG.md backlog into a task backlog (format v2)"),
)


def add_task_command_parsers(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Add the three commands; each takes a repository root and applies only with --write."""
    for name, text in COMMANDS:
        command = commands.add_parser(name, help=text)
        command.add_argument("path", nargs="?", default=".", help="repository root (default: .)")
        command.add_argument(
            "--write", action="store_true", help="apply instead of printing the plan"
        )
        if name == "migrate":
            command.add_argument(
                "--recover",
                action="store_true",
                help="bring into a migrated backlog what an older migrate lost (IDs, fields, "
                "text), read from git",
            )
            command.add_argument(
                "--from",
                dest="revision",
                metavar="REV",
                help="with --recover: the commit that still has TODO.md / TODO_LOG.md "
                "(default: the one before the commit that deleted them)",
            )
