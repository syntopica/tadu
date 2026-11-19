"""Read the command line, config files included, and settle the backlog a change targets."""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

from tadu.config_error import ConfigError
from tadu.parse_command_line import parse_command_line
from tadu.settle_target import settle_target
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    import argparse


def read_arguments(argv: list[str] | None, description: str | None) -> argparse.Namespace | int:
    """The parsed arguments, or the exit code (2) of a command line that cannot be used."""
    try:
        args = parse_command_line(argv, os.environ, description)
    except (ConfigError, WorkspaceError) as error:
        print(f"tadu: {error}", file=sys.stderr)
        return 2
    refused = settle_target(args)
    return args if refused is None else refused
