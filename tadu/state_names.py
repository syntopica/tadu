"""The name of each item state marker, as task files (format v2) write it."""

from __future__ import annotations

STATE_NAMES = {" ": "pending", "~": "in_progress", "!": "blocked", "x": "done", "-": "cancelled"}
