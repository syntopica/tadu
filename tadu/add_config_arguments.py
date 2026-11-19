"""Add the options that choose the config file."""

from __future__ import annotations

import argparse


def add_config_arguments(parser: argparse.ArgumentParser) -> None:
    """`--config FILE` or `--no-config`, left out of the namespace unless given.

    Every command takes them, as does `tadu` before the command.
    """
    choice = parser.add_mutually_exclusive_group()
    choice.add_argument(
        "--config",
        metavar="FILE",
        default=argparse.SUPPRESS,
        help="read option defaults from this file (default: $TADU_CONFIG, else config.toml "
        "in tadu's user config directory, such as ~/.config/tadu/config.toml)",
    )
    choice.add_argument(
        "--no-config",
        action="store_true",
        default=argparse.SUPPRESS,
        help="take no option from a config file: neither the user's nor the option tables "
        "of the workspace's local file",
    )
