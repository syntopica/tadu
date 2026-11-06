"""File names the board serves from its directory: lowercase, no path, a known extension."""

from __future__ import annotations

import re

BOARD_ASSET_NAME_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]*\.(js|css|html)")
