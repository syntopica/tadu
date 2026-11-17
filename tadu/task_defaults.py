"""Defaults of a task backlog: the "not decided yet" values and the policy numbers."""

from __future__ import annotations

UNKNOWN_PRIORITY = "untriaged"
UNKNOWN_CATEGORY = "general"
UNKNOWN_TYPE = "untriaged"
DEFAULT_TASK_TYPES = ("bug", "feature", "chore", "test", "docs", "refactor", "perf", "security")
STALE_AFTER_DAYS = 14
MONTH_FOLDERS_MIN = 10
