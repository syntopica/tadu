"""An option a config file may set, as the command line declares it."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse


@dataclass(frozen=True)
class ConfigSlot:
    """The option's argparse action, with the default and requiredness it was declared with.

    The action itself no longer has them: its default is SUPPRESS, so that an option the
    command line leaves out is missing from the parsed namespace, and it is never
    required, since a config file may give it.
    """

    action: argparse.Action
    default: object
    required: bool

    @property
    def flag(self) -> str:
        """The long option, such as `--public-url`."""
        return self.action.option_strings[0]
