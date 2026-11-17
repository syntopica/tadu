"""Rank a card's priority for sorting and thresholds."""

from __future__ import annotations

from tadu.task_priorities import TASK_PRIORITIES


def priority_rank(priority: str | None) -> int:
    """0 for urgent upwards; no priority ranks as untriaged, between high and normal."""
    return TASK_PRIORITIES.index(priority or "untriaged")
