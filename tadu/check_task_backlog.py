"""The doctor check for a task backlog (format v2)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from tadu.task_backlog_findings import task_backlog_findings

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.finding import Finding


def check_task_backlog(root: Path) -> tuple[Finding, ...]:
    """Every finding for the task backlog under root, judged against today's local date."""
    return task_backlog_findings(root, datetime.now(UTC).astimezone().date())
