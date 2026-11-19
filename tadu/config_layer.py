"""The options one config file gives a command."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from tadu.check_config_keys import check_config_keys
from tadu.check_top_level_keys import check_top_level_keys
from tadu.config_settings import DEFAULTS_TABLE
from tadu.config_tables import config_tables
from tadu.config_value import config_value
from tadu.local_keys import LOCAL_KEYS
from tadu.read_toml import read_toml

if TYPE_CHECKING:
    from tadu.config_slot import ConfigSlot


def config_layer(
    path: Path, command: str, slots: dict[str, ConfigSlot], *, local: bool
) -> dict[str, object]:
    """`[defaults]`, then the command's table, which wins; read as the command line reads.

    `local` is a workspace's local file, whose own keys sit beside the tables. A
    `workspace` is relative to the file's directory, and may start with `~`.
    """
    data = read_toml(path)
    if local:
        check_top_level_keys(data, LOCAL_KEYS, path)
    else:
        check_config_keys(data, path)
    tables = config_tables(data, path, local=local)
    values: dict[str, object] = {}
    for name in (DEFAULTS_TABLE, command):
        for key, raw in tables.get(name, {}).items():
            if key not in slots:
                continue
            value = config_value(slots[key], raw, f"{path}: [{name}] {key}")
            if key == "workspace":
                value = str(path.parent / Path(str(value)).expanduser())
            # keys: the command's options this file sets; its own table after [defaults]
            values[key] = value
    return values
