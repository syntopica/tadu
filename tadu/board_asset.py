"""The board page's static files."""

from __future__ import annotations

from importlib.resources import files

from tadu.board_content_types import BOARD_CONTENT_TYPES


def board_asset(name: str) -> tuple[bytes, str] | None:
    """The bytes and content type of a known asset; None for any other name."""
    content_type = BOARD_CONTENT_TYPES.get(name)
    if content_type is None:
        return None
    return (files("tadu") / "board" / name).read_bytes(), content_type
