"""A config file that cannot be used."""

from __future__ import annotations


class ConfigError(Exception):
    """The message names the file, the table and the option at fault."""
