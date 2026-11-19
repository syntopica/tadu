"""Argparse type for the address people open the board at."""

from __future__ import annotations

import argparse
import re
from urllib.parse import urlsplit

from tadu.board_asset_name_pattern import BOARD_ASSET_NAME_PATTERN

DEFAULT_PORTS = {"http": 80, "https": 443}
SEGMENT = re.compile(r"[A-Za-z0-9._~-]+")
# First path segments the board's own routes use: a board served there could not tell
# its prefix from its routes once a proxy had taken the prefix away.
RESERVED = frozenset({"api", "auth"})


def public_board_url(text: str) -> str:
    """An http or https URL of a host, on its own or with a path, as `scheme://host[:port][/path]`.

    The host is lowercased and a default port left out, as a browser's Host header has
    them; a trailing slash goes. A path is a board served in a subfolder, such as
    https://example.com/tadu: its segments are plain names, and the first is neither
    `api`, `auth` nor a file name of the board's page.
    """
    parts = urlsplit(text.strip())
    try:
        port = parts.port
    except ValueError:
        port = -1
    path = parts.path.rstrip("/")
    segments = path.split("/")[1:] if path else []
    if (
        parts.scheme not in DEFAULT_PORTS
        or not parts.hostname
        or port == -1
        or "@" in parts.netloc
        or parts.query
        or parts.fragment
        or any(not SEGMENT.fullmatch(s) or s in {".", ".."} for s in segments)
        or (
            segments
            and (segments[0] in RESERVED or BOARD_ASSET_NAME_PATTERN.fullmatch(segments[0]))
        )
    ):
        msg = (
            "must be http:// or https://, a host and maybe a path, such as "
            f"https://board.example.com or https://example.com/tadu: {text}"
        )
        raise argparse.ArgumentTypeError(msg)
    shown = "" if port in {None, DEFAULT_PORTS[parts.scheme]} else f":{port}"
    return f"{parts.scheme}://{parts.hostname}{shown}{path}"
