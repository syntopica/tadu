"""Pick the doctor checks for a repository's backlog format."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.check_history_index import check_history_index
from tadu.check_rule_block import check_rule_block
from tadu.check_task_backlog import check_task_backlog
from tadu.doctor_checks import DOCTOR_CHECKS
from tadu.is_task_backlog import is_task_backlog

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from tadu.finding import Finding


def doctor_checks_for(root: Path) -> tuple[Callable[[Path], tuple[Finding, ...]], ...]:
    """The task backlog checks when root holds todo/tadu.json, else the Markdown checks."""
    if is_task_backlog(root):
        return (check_task_backlog, check_history_index, check_rule_block)
    return DOCTOR_CHECKS
