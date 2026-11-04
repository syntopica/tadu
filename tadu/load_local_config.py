"""Load the untracked per-machine configuration of a directory."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.local_config import LocalConfig
from tadu.optional_text import optional_text
from tadu.parse_paths import parse_paths
from tadu.read_toml import read_toml
from tadu.workspace_error import WorkspaceError
from tadu.workspace_file_names import LOCAL_FILE

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.workspace import Workspace


def load_local_config(directory: Path, workspace: Workspace) -> LocalConfig:
    """Parse the local file; a missing file gives an empty configuration."""
    path = directory / LOCAL_FILE
    if not path.exists():
        return LocalConfig({}, None, None)
    data = read_toml(path)
    me = optional_text(data, "local", "me")
    if me is not None and me not in {p.id for p in workspace.people}:
        msg = f"me: unknown person {me}"
        raise WorkspaceError(msg)
    return LocalConfig(
        parse_paths(data.get("paths"), directory, workspace),
        me,
        optional_text(data, "local", "editor_url"),
    )
