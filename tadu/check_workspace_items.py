"""Check the items of every repository of a workspace."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from tadu.duplicate_id_findings import duplicate_id_findings
from tadu.finding import Finding
from tadu.load_local_config import load_local_config
from tadu.load_workspace import load_workspace
from tadu.scan_problem_findings import scan_problem_findings
from tadu.unknown_assignee_findings import unknown_assignee_findings
from tadu.workspace_cards import workspace_cards
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    from datetime import date
    from pathlib import Path


def check_workspace_items(directory: Path, today: date) -> tuple[Finding, ...]:
    """Assignee, duplicate-ID and scan findings; a bad workspace is one error."""
    try:
        workspace = load_workspace(directory)
        local = load_local_config(directory, workspace)
    except WorkspaceError as error:
        return (Finding("W004", "error", str(directory), 0, str(error)),)
    cards, problems = workspace_cards(workspace, local, today - timedelta(days=14))
    return (
        *unknown_assignee_findings(workspace, local, cards),
        *duplicate_id_findings(local, cards),
        *scan_problem_findings(problems),
    )
