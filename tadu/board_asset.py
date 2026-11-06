"""The board page's static files."""

from __future__ import annotations

from importlib.resources import files

from tadu.board_asset_name_pattern import BOARD_ASSET_NAME_PATTERN
from tadu.board_content_types import BOARD_CONTENT_TYPES


def board_asset(name: str) -> tuple[bytes, str] | None:
    """The bytes and content type of a file directly in the board directory; None otherwise."""
    match = BOARD_ASSET_NAME_PATTERN.fullmatch(name)
    if match is None:
        return None
    resource = files("tadu") / "board" / name
    if not resource.is_file():
        return None
    return resource.read_bytes(), BOARD_CONTENT_TYPES[match.group(1)]
