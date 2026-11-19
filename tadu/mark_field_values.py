"""The item fields a parsed add or mark sets."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.list_values import list_values
from tadu.mark_fields import MARK_FIELDS

if TYPE_CHECKING:
    import argparse


def mark_field_values(args: argparse.Namespace) -> tuple[tuple[str, str], ...]:
    """Field name and text of each field given: lists joined by `, `, numbers as digits."""
    found: list[tuple[str, str]] = []
    for name, flag in MARK_FIELDS:
        value = getattr(args, flag)
        text = ", ".join(list_values(value)) if isinstance(value, list) else value
        if text is not None and text != "":
            found.append((name, str(text)))
    return tuple(found)
