"""The tables of a config file that set command options."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.config_error import ConfigError
from tadu.config_settings import CONFIG_OPTIONS, DEFAULTS_TABLE

if TYPE_CHECKING:
    from pathlib import Path

EVERY_KEY = frozenset(key for keys in CONFIG_OPTIONS.values() for key in keys)


def config_tables(
    data: dict[str, object], path: Path, *, local: bool
) -> dict[str, dict[str, object]]:
    """`[defaults]` and each command's table, by name; ConfigError for a key no command takes.

    `[defaults]` takes any option some command takes. A workspace's local file cannot
    name a workspace: it is the workspace's own.
    """
    tables: dict[str, dict[str, object]] = {}
    for name in (DEFAULTS_TABLE, *CONFIG_OPTIONS):
        table = data.get(name)
        if table is None:
            continue
        if not isinstance(table, dict):
            msg = f"{path}: {name} must be a table, [{name}]"
            raise ConfigError(msg)
        allowed = EVERY_KEY if name == DEFAULTS_TABLE else frozenset(CONFIG_OPTIONS[name])
        allowed -= {"workspace"} if local else set()
        unknown = sorted(set(table) - allowed)
        if unknown:
            key = unknown[0]
            hint = (
                f"write {key.replace('-', '_')}"
                if key.replace("-", "_") in allowed
                else (f"[{name}] takes {', '.join(sorted(allowed))}")
            )
            msg = f"{path}: [{name}] {key}: a config file cannot set it here; {hint}"
            raise ConfigError(msg)
        # keys: each table the file has, by its name
        tables[name] = table
    return tables
