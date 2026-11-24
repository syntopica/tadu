"""Recognize explicit requests about a project's backlog."""

from __future__ import annotations

import re


def backlog_prompt(prompt: str) -> bool:
    """Match English and Spanish backlog requests without routing ordinary coding reviews."""
    return bool(
        re.search(
            r"\b(backlog|pending tasks?|tareas? pendientes?|pendientes?)\b"
            r"|\b(?:el|los|my|the|review|show)\s+(?:todos?|to-do)\b"
            r"|\btodo(?:\.md|_log\.md)\b",
            prompt,
            re.IGNORECASE,
        )
    )
