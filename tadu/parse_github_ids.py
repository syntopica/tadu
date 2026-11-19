"""Read the text of a board's learned GitHub ids."""

from __future__ import annotations

import json

VERSION = 1


def parse_github_ids(text: str) -> dict[str, int]:
    """The GitHub id of each repository key; ValueError for anything but the written shape.

    The shape is `{"version": 1, "github_ids": {"<key>": <id above 0>, ...}}`. Nothing is
    guessed: a file that says something else protects nothing, so it is an error.
    """
    data = json.loads(text)
    ids = data.get("github_ids") if isinstance(data, dict) else None
    if not isinstance(data, dict) or data.get("version") != VERSION or not isinstance(ids, dict):
        msg = f'expected {{"version": {VERSION}, "github_ids": {{...}}}}'
        raise ValueError(msg)
    for key, value in ids.items():
        if type(value) is not int or value <= 0:
            msg = f"github id of {key} must be a whole number above 0"
            raise ValueError(msg)
    return ids
