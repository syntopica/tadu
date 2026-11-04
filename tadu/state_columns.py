"""Board column of each state marker other than open."""

from __future__ import annotations

STATE_COLUMNS = {"~": "in_progress", "!": "blocked", "x": "done", "-": "cancelled"}
