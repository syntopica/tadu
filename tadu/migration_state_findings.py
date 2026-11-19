"""Findings about a migration to a task backlog that is not finished."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.finding import Finding
from tadu.pending_recovery import PENDING_KEY
from tadu.todo_layout import TODO_CONFIG, TODO_DIR
from tadu.v1_texts import V1_FILES

if TYPE_CHECKING:
    from pathlib import Path


def migration_state_findings(root: Path, config: dict[str, object]) -> list[Finding]:
    """C005 for a recovery started and not finished, C004 for each Markdown file left beside."""
    findings: list[Finding] = []
    pending = config.get(PENDING_KEY)
    if isinstance(pending, str):
        message = (
            f"tadu migrate --recover from {pending[:12]} started and has not finished (stopped, "
            "or refused something); run it again to finish it"
        )
        findings.append(Finding("C005", "warning", str(root / TODO_DIR / TODO_CONFIG), 0, message))
    for name in V1_FILES:
        if (root / name).is_file():
            message = (
                f"{name} is ignored next to a task backlog; tadu migrate --write brings what it "
                "holds into todo/ and removes it"
            )
            findings.append(Finding("C004", "warning", str(root / name), 0, message))
    return findings
