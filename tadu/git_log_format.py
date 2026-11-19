"""The commit header tadu asks `git log` for."""

from __future__ import annotations

RECORD = "\x1e"
UNIT = "\x1f"
GIT_LOG_FORMAT = f"--format={RECORD}%H{UNIT}%P{UNIT}%aI{UNIT}%an{UNIT}%s"
