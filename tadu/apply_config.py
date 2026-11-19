"""Give a command the options its command line left out."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.config_error import ConfigError
from tadu.config_settings import COMMAND_LINE
from tadu.config_values import config_values

if TYPE_CHECKING:
    import argparse
    from collections.abc import Mapping

    from tadu.config_slot import ConfigSlot


def apply_config(
    args: argparse.Namespace, slots: dict[str, ConfigSlot], environ: Mapping[str, str]
) -> None:
    """Fill each of `slots` the command line did not give: from config files, else its default.

    `args.option_sources` then says where each option that is not a default came from:
    COMMAND_LINE, or the path of a config file. With `--no-config`, no file is read.
    ConfigError for a file that cannot be used.
    """
    skip = getattr(args, "no_config", False)
    if skip and hasattr(args, "config"):
        msg = "give --config or --no-config, not both"
        raise ConfigError(msg)
    values = {} if skip or not slots else config_values(args, slots, environ)
    sources: dict[str, str] = {}
    for key, slot in slots.items():
        if hasattr(args, slot.action.dest):
            # keys: one entry per option of the command
            sources[key] = COMMAND_LINE
        elif key in values:
            value, path = values[key]
            setattr(args, slot.action.dest, value)
            # keys: one entry per option of the command
            sources[key] = str(path)
        else:
            setattr(args, slot.action.dest, slot.default)
    args.option_sources = sources
