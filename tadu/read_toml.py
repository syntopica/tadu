"""Read one workspace TOML file and check its format version."""

from __future__ import annotations

import tomllib
from typing import TYPE_CHECKING

from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    from pathlib import Path


def read_toml(path: Path) -> dict[str, object]:
    """Parse the file; a missing file, bad TOML or a version other than 1 is an error."""
    try:
        with path.open("rb") as handle:
            data: dict[str, object] = tomllib.load(handle)
    except (OSError, ValueError) as error:
        msg = f"{path}: {error}"
        raise WorkspaceError(msg) from error
    version = data.get("version")
    if isinstance(version, bool) or version != 1:
        msg = f"{path}: version must be 1"
        raise WorkspaceError(msg)
    return data
