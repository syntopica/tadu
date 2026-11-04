"""Editor link for a line of a file."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def editor_line_url(template: str | None, absolute: Path, line: int) -> str | None:
    """The template filled with path and line; None without or with a bad template."""
    if template is None:
        return None
    try:
        return template.format(path=str(absolute), line=line)
    except (KeyError, IndexError, ValueError):
        return None
