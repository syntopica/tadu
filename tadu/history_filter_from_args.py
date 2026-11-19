"""The history filter a command line asks for."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.history_filter import HistoryFilter

if TYPE_CHECKING:
    import argparse

FIELD_ALIASES = {"assignee": "assignees", "label": "labels"}


def history_filter_from_args(args: argparse.Namespace) -> HistoryFilter:
    """`--field`, `--since`, `--until` and `--author`; all absent is the empty filter.

    `--field` repeats or takes a comma-separated list; `assignee` and `label` name the list
    fields `assignees` and `labels`.
    """
    names = (name.strip() for value in args.field for name in value.split(","))
    fields = frozenset(FIELD_ALIASES.get(name, name) for name in names if name)
    return HistoryFilter(fields, args.since, args.until, args.author or None)
