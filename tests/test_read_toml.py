from pathlib import Path

import pytest

from tadu.read_toml import read_toml
from tadu.workspace_error import WorkspaceError


def test_reads_version_one(tmp_path: Path) -> None:
    path = tmp_path / "a.toml"
    path.write_text('version = 1\nname = "x"\n')
    assert read_toml(path) == {"version": 1, "name": "x"}


def test_missing_file(tmp_path: Path) -> None:
    path = tmp_path / "a.toml"
    with pytest.raises(WorkspaceError, match=f"^{path}: "):
        read_toml(path)


def test_invalid_toml(tmp_path: Path) -> None:
    path = tmp_path / "a.toml"
    path.write_text("version = [")
    with pytest.raises(WorkspaceError, match=f"^{path}: "):
        read_toml(path)


@pytest.mark.parametrize("text", ["version = 2", "", "version = true", 'version = "1"'])
def test_wrong_version(tmp_path: Path, text: str) -> None:
    path = tmp_path / "a.toml"
    path.write_text(text)
    with pytest.raises(WorkspaceError, match="version"):
        read_toml(path)
