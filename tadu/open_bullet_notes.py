"""The log bullets of an open legacy item, kept as notes."""

from __future__ import annotations


def open_bullet_notes(bullets: dict[str, list[str]]) -> list[str]:
    """One `Name: text` line per Result, Evidence and Resolution bullet, which an open task cannot hold."""
    return [
        f"{name}: {text}"
        for name in ("Result", "Evidence", "Resolution")
        for text in bullets.get(name, [])
        if text
    ]
