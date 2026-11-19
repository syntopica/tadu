import argparse
from pathlib import Path

import pytest

from tadu.target_path import target_path
from tadu.workspace_error import WorkspaceError


def args(
    paths: list[str], workspace: str | None = None, repository: str | None = None
) -> argparse.Namespace:
    return argparse.Namespace(paths=paths, workspace=workspace, repository=repository)


def workspace(root: Path, access: str) -> Path:
    (root / "shop").mkdir()
    (root / "tadu-workspace.toml").write_text(
        f'version = 1\n[[repository]]\nkey = "shop"\naccess = "{access}"\n'
    )
    (root / "tadu-workspace.local.toml").write_text(
        f'version = 1\n[paths]\nshop = "{root / "shop"}"\n'
    )
    return root


def test_one_root_as_given() -> None:
    assert target_path(args([]), "write") == "."
    assert target_path(args(["../shop"]), "write") == "../shop"


def test_one_of_several_roots(tmp_path: Path) -> None:
    roots = [str(tmp_path / "shop"), str(tmp_path / "web")]
    assert target_path(args(roots, repository="web"), "write") == str(tmp_path / "web")
    with pytest.raises(WorkspaceError, match="several repositories"):
        target_path(args(roots), "write")


def test_a_workspace_repository_within_its_access(tmp_path: Path) -> None:
    root = workspace(tmp_path, "write")
    assert target_path(args([], str(root)), "write") == str(root / "shop")
    with pytest.raises(
        WorkspaceError, match="repository shop allows write only, and this needs admin"
    ):
        target_path(args([], str(root), "shop"), "admin")
    with pytest.raises(WorkspaceError, match="not both"):
        target_path(args(["x"], str(root)), "write")
