"""Detect the five-state legend."""

from __future__ import annotations

from tadu.state_markers import STATE_MARKERS


def has_state_legend(text: str) -> bool:
    """True when every state marker is quoted somewhere in the text."""
    return all(marker in text for marker in STATE_MARKERS)
