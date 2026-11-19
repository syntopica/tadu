"""Read the `--event` values of `tadu changes`."""

from __future__ import annotations

import argparse

from tadu.change_events import CHANGE_EVENTS


def change_event_list(value: str) -> tuple[str, ...]:
    """The events of one comma-separated value; ArgumentTypeError names any unknown one."""
    names = tuple(name.strip() for name in value.split(",") if name.strip())
    unknown = [name for name in names if name not in CHANGE_EVENTS]
    if unknown:
        msg = f"unknown event {', '.join(unknown)}; choose from {', '.join(CHANGE_EVENTS)}"
        raise argparse.ArgumentTypeError(msg)
    return names
