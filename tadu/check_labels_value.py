"""Validate a Labels field value."""

from __future__ import annotations

from tadu.label_pattern import LABEL_PATTERN
from tadu.split_list_value import split_list_value


def check_labels_value(value: str) -> str | None:
    """A problem message, or None when every label is a lowercase slug."""
    if all(LABEL_PATTERN.match(label) for label in split_list_value(value)):
        return None
    return "Labels holds a value that is not a lowercase slug"
