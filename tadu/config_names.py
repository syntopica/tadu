"""Read a set of names declared in a task backlog's configuration."""

from __future__ import annotations


def config_names(config: dict[str, object], key: str) -> frozenset[str]:
    """The keys of an object value or the strings of a list value; empty when absent or neither."""
    value = config.get(key)
    if isinstance(value, dict):
        return frozenset(str(name) for name in value)
    if isinstance(value, list):
        return frozenset(item for item in value if isinstance(item, str))
    return frozenset()
