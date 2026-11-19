"""The values of a repeatable, comma-separable argument."""

from __future__ import annotations

from tadu.split_list_value import split_list_value


def list_values(values: list[str] | None) -> list[str]:
    """Every stripped, non-empty part, in order: `--label a,b --label c` gives a, b and c."""
    return [part for value in values or () for part in split_list_value(value)]
