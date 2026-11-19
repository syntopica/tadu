"""A tool call's arguments under the names its schema uses."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.param_aliases import param_aliases

if TYPE_CHECKING:
    from tadu.param import Param


def canonical_arguments(params: tuple[Param, ...], arguments: object) -> object:
    """The arguments with each alias renamed and one text given for a list made a list of it.

    So `notes` reads as `note` and `"note": "x"` as `["x"]`. Anything that is not an object,
    and names no argument knows, is left for the schema check to refuse; an argument given
    under two names keeps the second as it was given, so that check refuses it as unknown.
    """
    if not isinstance(arguments, dict):
        return arguments
    # keys: one entry per alias, and test_operations checks no alias names two arguments.
    owners = {alias: param for param in params for alias in param_aliases(param)}
    lists = {param.name for param in params if param.kind in ("list", "words")}
    found: dict[str, object] = {}
    for key, value in arguments.items():
        owner = owners.get(key)
        name = key
        if owner is not None and owner.name not in arguments and owner.name not in found:
            name = owner.name
        # keys: an alias is renamed only when its argument's own name is not given nor taken.
        found[name] = [value] if name in lists and isinstance(value, str) else value
    return found
