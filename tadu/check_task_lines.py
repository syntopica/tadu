"""Validate a Markdown value stored as an array of lines."""

from __future__ import annotations

from tadu.is_one_line import is_one_line


def check_task_lines(value: object) -> str | None:
    """A message unless the value is a non-empty list of strings without line breaks.

    An empty string is a blank line; readers join the elements with a newline.
    """
    if not isinstance(value, list) or not value:
        return "must be a non-empty list of lines"
    if not all(isinstance(line, str) and is_one_line(line) for line in value):
        return "must be a list of strings without line breaks, one per line"
    return None
