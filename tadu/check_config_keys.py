"""Check the top level of a user's config file."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.config_error import ConfigError
from tadu.config_settings import CONFIG_OPTIONS, DEFAULTS_TABLE

if TYPE_CHECKING:
    from pathlib import Path


def check_config_keys(data: dict[str, object], path: Path) -> None:
    """ConfigError for anything but `version`, `[defaults]` and the tables of commands.

    Commands without a table (close, mark, set and the like) take nothing from a file:
    what a call acts on, and whether it writes, stay on the command line.
    """
    unknown = sorted(set(data) - {"version", DEFAULTS_TABLE, *CONFIG_OPTIONS})
    if unknown:
        msg = (
            f"{path}: {unknown[0]}: a config file has version, [{DEFAULTS_TABLE}] and the "
            f"tables {', '.join(f'[{name}]' for name in CONFIG_OPTIONS)}"
        )
        raise ConfigError(msg)
