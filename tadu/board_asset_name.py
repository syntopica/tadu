"""The board file a URL path asks for."""

from __future__ import annotations

INDEX = "index.html"


def board_asset_name(path: str) -> str:
    """index.html for "/" only; otherwise the path without its leading slash, or ""."""
    if path == "/":
        return INDEX
    name = path.removeprefix("/")
    if name in (path, INDEX):
        return ""
    return name
