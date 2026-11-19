from pathlib import Path

import pytest

from tadu.change_repositories import change_repositories
from tadu.change_repository import ChangeRepository
from tadu.scan_problem import ScanProblem
from tadu.scope import Scope
from tadu.workspace_error import WorkspaceError


def test_roots_given_as_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("one/api", "two/api", "web"):
        (tmp_path / name).mkdir(parents=True)
    found, problems = change_repositories(Scope((str(tmp_path / "one/api"), str(tmp_path / "web"))))
    assert found == (
        ChangeRepository("api", None, tmp_path / "one/api"),
        ChangeRepository("web", None, tmp_path / "web"),
    )
    assert problems == ()
    web = change_repositories(
        Scope((str(tmp_path / "web"), str(tmp_path / "two/api")), None, "web")
    )
    assert web == ((ChangeRepository("web", None, tmp_path / "web"),), ())
    monkeypatch.chdir(tmp_path / "web")
    assert change_repositories(Scope())[0] == (ChangeRepository("web", None, tmp_path / "web"),)


def test_workspace_with_a_project_and_a_missing_checkout(tmp_path: Path) -> None:
    (tmp_path / "tadu-workspace.toml").write_text(
        'version = 1\n[[repository]]\nkey = "shop"\nbacklog = "app"\n[[repository]]\nkey = "gone"\n'
        '[[project]]\nkey = "store"\nrepositories = ["shop"]\n'
    )
    (tmp_path / "tadu-workspace.local.toml").write_text(
        f'version = 1\n[paths]\nshop = "{tmp_path}"\n'
    )
    found, problems = change_repositories(Scope(workspace=str(tmp_path)))
    assert found == (ChangeRepository("shop", "store", tmp_path, "app"),)
    assert problems == (ScanProblem("gone", "no checkout path in tadu-workspace.local.toml"),)
    only = change_repositories(Scope(workspace=str(tmp_path), repository="shop"))
    assert only == ((ChangeRepository("shop", "store", tmp_path, "app"),), ())


def test_both_or_a_broken_workspace(tmp_path: Path) -> None:
    with pytest.raises(WorkspaceError, match="not both"):
        change_repositories(Scope(("x",), str(tmp_path)))
    with pytest.raises(WorkspaceError):
        change_repositories(Scope(workspace=str(tmp_path)))
