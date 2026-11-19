"""The `--version` option, which reads the installed version only when it is asked for."""

from __future__ import annotations

import argparse
import sys
from typing import override


class VersionAction(argparse.Action):
    """Print `tadu <version>` and exit, like argparse's own version action.

    importlib.metadata is imported here, not with the parser: it costs more than the
    rest of the parser together, and every other command would pay for it.
    """

    def __init__(self, option_strings: list[str], dest: str, **kwargs: object) -> None:  # noqa: ARG002 - argparse passes what it passes every action
        """Take no value, like a flag."""
        super().__init__(option_strings, dest, nargs=0, help="show the version and exit")

    @override
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: object,
        option_string: str | None = None,
    ) -> None:
        """Print the version and exit."""
        from importlib.metadata import version  # noqa: PLC0415 - only when asked for

        sys.stdout.write(f"tadu {version('tadu')}\n")
        parser.exit()
