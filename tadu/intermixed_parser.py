"""A subcommand parser that takes options between its positionals."""

from __future__ import annotations

import argparse
from typing import TYPE_CHECKING, override

if TYPE_CHECKING:
    from collections.abc import Sequence

HELD = "\0tadu-positional-"


class IntermixedParser(argparse.ArgumentParser):
    """Parses as parse_intermixed_args does, so `show KEY --history ROOT` reads ROOT as a root.

    A plain parser matches the positionals in one go, before the options that separate them,
    and then refuses ROOT. Only for subcommands: intermixed parsing refuses subparsers.
    Words after `--` stay positionals even when they start with `-`, which intermixed parsing
    alone would read as unknown options: they are held aside while it parses.
    """

    mixing = False

    @override
    def parse_known_args(  # type: ignore[override]
        self, args: Sequence[str] | None = None, namespace: argparse.Namespace | None = None
    ) -> tuple[argparse.Namespace, list[str]]:
        """Intermixed, except for the plain parses that intermixed parsing itself makes."""
        if self.mixing or args is None:
            return super().parse_known_args(args, namespace)
        words = list(args)
        cut = words.index("--") + 1 if "--" in words else len(words)
        # keys: one per position after `--`, each with its own index.
        held = {f"{HELD}{at}": word for at, word in enumerate(words[cut:])}
        self.mixing = True
        try:
            parsed, extra = self.parse_known_intermixed_args([*words[:cut], *held], namespace)
        finally:
            self.mixing = False
        for name, value in vars(parsed).items():
            if isinstance(value, str) and value in held:
                setattr(parsed, name, held[value])
            elif isinstance(value, list):
                setattr(
                    parsed,
                    name,
                    [held.get(item, item) if isinstance(item, str) else item for item in value],
                )
        return parsed, [held.get(word, word) for word in extra]
