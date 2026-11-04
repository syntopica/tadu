from pathlib import Path

import pytest

from tadu.parse_paths import parse_paths
from tadu.repository_entry import RepositoryEntry
from tadu.workspace import Workspace
from tadu.workspace_error import WorkspaceError


def workspace(directory: Path) -> Workspace:
    return Workspace(directory, (RepositoryEntry("shop", None),), (), (), ())


def test_absent_table_is_empty(tmp_path: Path) -> None:
    assert parse_paths(None, tmp_path, workspace(tmp_path)) == {}


def test_relative_value_is_normalised(tmp_path: Path) -> None:
    (tmp_path / "ws").mkdir()
    paths = parse_paths({"shop": "../shop"}, tmp_path / "ws", workspace(tmp_path))
    assert paths == {"shop": (tmp_path / "shop").resolve()}
    assert ".." not in paths["shop"].parts


def test_tilde_expands_to_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    paths = parse_paths({"shop": "~/x"}, Path("/elsewhere"), workspace(tmp_path))
    assert paths == {"shop": (tmp_path / "x").resolve()}


def test_absolute_value_ignores_the_directory(tmp_path: Path) -> None:
    paths = parse_paths({"shop": str(tmp_path)}, Path("/elsewhere"), workspace(tmp_path))
    assert paths == {"shop": tmp_path.resolve()}


def test_unknown_key_and_non_table_are_errors(tmp_path: Path) -> None:
    with pytest.raises(WorkspaceError, match="unknown repository ghost"):
        parse_paths({"ghost": "x"}, tmp_path, workspace(tmp_path))
    with pytest.raises(WorkspaceError, match="must be a table"):
        parse_paths("x", tmp_path, workspace(tmp_path))
    with pytest.raises(WorkspaceError, match="shop must be a string"):
        parse_paths({"shop": 1}, tmp_path, workspace(tmp_path))
