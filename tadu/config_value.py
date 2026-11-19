"""Read one option's value from a config file as the command line would."""

from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

from tadu.config_error import ConfigError

if TYPE_CHECKING:
    from tadu.config_slot import ConfigSlot


def config_value(slot: ConfigSlot, raw: object, where: str) -> object:
    """The value the option would get from the command line; ConfigError when it is wrong.

    A switch such as `json` takes true or false. Any other option takes a string or a
    whole number, read by the same type and choices as its flag, so a config file is held
    to the rules of the command line. `where` names the file, table and key.
    """
    action = slot.action
    if isinstance(action, argparse.BooleanOptionalAction):
        if not isinstance(raw, bool):
            msg = f"{where}: must be true or false"
            raise ConfigError(msg)
        return raw
    if isinstance(raw, bool) or not isinstance(raw, str | int):
        msg = f"{where}: must be a string or a whole number"
        raise ConfigError(msg)
    try:
        value = action.type(str(raw)) if callable(action.type) else str(raw)
    except (argparse.ArgumentTypeError, ValueError) as error:
        msg = f"{where}: {error}"
        raise ConfigError(msg) from None
    if action.choices is not None and value not in action.choices:
        msg = f"{where}: must be one of {', '.join(map(str, action.choices))}, not {raw}"
        raise ConfigError(msg)
    return value
