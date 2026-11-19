"""Write a board's learned GitHub ids as text."""

from __future__ import annotations

import json

from tadu.parse_github_ids import VERSION


def render_github_ids(ids: dict[str, int]) -> str:
    """Keys sorted, one per line, so the file reads well in a diff if it is committed."""
    data = {"version": VERSION, "github_ids": dict(sorted(ids.items()))}
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"
