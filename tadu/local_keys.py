"""Top-level keys and tables a local workspace file may hold.

Besides its own keys, the tables of command options a config file has: options for the
commands run on this workspace.
"""

from __future__ import annotations

from tadu.config_settings import CONFIG_OPTIONS, DEFAULTS_TABLE

LOCAL_KEYS = frozenset({"version", "me", "editor_url", "paths", DEFAULTS_TABLE, *CONFIG_OPTIONS})
