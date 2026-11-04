"""Load the shared workspace file of a directory."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.parse_organization import parse_organization
from tadu.parse_person import parse_person
from tadu.parse_project import parse_project
from tadu.parse_repository import parse_repository
from tadu.read_toml import read_toml
from tadu.table_rows import table_rows
from tadu.workspace import Workspace
from tadu.workspace_error import WorkspaceError
from tadu.workspace_file_names import WORKSPACE_FILE
from tadu.workspace_problems import workspace_problems

if TYPE_CHECKING:
    from pathlib import Path


def load_workspace(directory: Path) -> Workspace:
    """Parse the workspace file; all problems come back in one error."""
    data = read_toml(directory / WORKSPACE_FILE)
    workspace = Workspace(
        directory,
        tuple(parse_repository(r) for r in table_rows(data, "repository")),
        tuple(parse_project(r) for r in table_rows(data, "project")),
        tuple(parse_organization(r) for r in table_rows(data, "organization")),
        tuple(parse_person(r) for r in table_rows(data, "person")),
    )
    problems = workspace_problems(workspace)
    if problems:
        raise WorkspaceError("; ".join(problems))
    return workspace
