from pathlib import Path

import pytest

from tadu.load_workspace import load_workspace
from tadu.scope import Scope
from tadu.workspace_error import WorkspaceError
from tadu.workspace_repository import workspace_repository


def test_a_key_checked_out_or_not_or_a_checkout_by_its_path(tmp_path: Path) -> None:
    (tmp_path / "shop").mkdir()
    (tmp_path / "tadu-workspace.toml").write_text(
        'version = 1\n[[repository]]\nkey = "shop"\n[[repository]]\nkey = "gone"\n'
    )
    (tmp_path / "tadu-workspace.local.toml").write_text(
        f'version = 1\n[paths]\nshop = "{tmp_path / "shop"}"\n'
    )
    loaded = load_workspace(tmp_path)
    scope = Scope(workspace=str(tmp_path))
    assert workspace_repository(Scope(workspace=str(tmp_path), repository="gone"), loaded) == "gone"
    by_path = Scope(workspace=str(tmp_path), repository=str(tmp_path / "shop"))
    assert workspace_repository(by_path, loaded) == "shop"
    with pytest.raises(WorkspaceError, match="no repository nope"):
        workspace_repository(Scope(workspace=scope.workspace, repository="nope"), loaded)
