"""Make the options a config file may set tell whether the command line gave them."""

from __future__ import annotations

import argparse

from tadu.config_settings import CONFIG_OPTIONS
from tadu.config_slot import ConfigSlot


def config_slots(
    commands: dict[str, argparse.ArgumentParser],
) -> dict[str, dict[str, ConfigSlot]]:
    """Each command's settable options by config key (`public_url` for `--public-url`).

    Their actions default to SUPPRESS and are not required, so that after parsing, an
    option is in the namespace only when the command line gave it; the declared default
    and requiredness move to the slot, for a config file to stand in for them.
    """
    slots: dict[str, dict[str, ConfigSlot]] = {}
    for command, keys in CONFIG_OPTIONS.items():
        # argparse has no public way to look an action up; this is the table it uses.
        actions = commands[command]._option_string_actions  # noqa: SLF001
        # keys: CONFIG_OPTIONS names each command once
        slots[command] = {}
        for key in keys:
            action = actions["--" + key.replace("_", "-")]
            # keys: one slot per settable option of the command, by its config key
            slots[command][key] = ConfigSlot(action, action.default, action.required)
            action.default, action.required = argparse.SUPPRESS, False
    return slots
