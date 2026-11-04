from pathlib import Path

import pytest

from tadu.load_local_config import load_local_config
from tadu.person_entry import PersonEntry
from tadu.repository_entry import RepositoryEntry
from tadu.workspace import Workspace
from tadu.workspace_error import WorkspaceError


def workspace(directory: Path) -> Workspace:
    return Workspace(
        directory,
        (RepositoryEntry("shop", None),),
        (),
        (),
        (PersonEntry("ana", "Ana", None),),
    )


def write(directory: Path, text: str) -> None:
    (directory / "tadu-workspace.local.toml").write_text(text)


def test_missing_file_gives_empty_config(tmp_path: Path) -> None:
    config = load_local_config(tmp_path, workspace(tmp_path))
    assert (config.paths, config.me, config.editor_url) == ({}, None, None)


def test_loads_values(tmp_path: Path) -> None:
    write(
        tmp_path,
        'version = 1\nme = "ana"\neditor_url = "vscode://file/{path}:{line}"\n'
        '[paths]\nshop = "../shop"\n',
    )
    config = load_local_config(tmp_path, workspace(tmp_path))
    assert config.paths == {"shop": tmp_path / "../shop"}
    assert config.me == "ana"
    assert config.editor_url == "vscode://file/{path}:{line}"


def test_version_only(tmp_path: Path) -> None:
    write(tmp_path, "version = 1\n")
    assert load_local_config(tmp_path, workspace(tmp_path)).paths == {}


@pytest.mark.parametrize(
    ("body", "fragment"),
    [
        ('[paths]\nghost = "x"\n', "paths: unknown repository ghost"),
        ('me = "ghost"\n', "me: unknown person ghost"),
        ("me = 1\n", "me"),
        ("editor_url = 1\n", "editor_url"),
        ("paths = 'x'\n", "paths"),
        ("[paths]\nshop = 1\n", "paths: shop"),
    ],
)
def test_bad_values(tmp_path: Path, body: str, fragment: str) -> None:
    write(tmp_path, "version = 1\n" + body)
    with pytest.raises(WorkspaceError, match=fragment):
        load_local_config(tmp_path, workspace(tmp_path))


@pytest.mark.parametrize(
    ("body", "name"),
    [('[local]\nme = "ana"\n', "local"), ("theme = 'dark'\n", "theme")],
)
def test_unknown_top_level_key_or_table_is_an_error(tmp_path: Path, body: str, name: str) -> None:
    write(tmp_path, "version = 1\n" + body)
    with pytest.raises(WorkspaceError, match=f"unknown top-level key {name}"):
        load_local_config(tmp_path, workspace(tmp_path))
