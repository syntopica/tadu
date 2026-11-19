from pathlib import Path

import pytest

from tadu.doctor_roots import doctor_roots
from tadu.scope import Scope
from tadu.workspace_error import WorkspaceError


def test_roots_as_given_or_the_current_directory(tmp_path: Path) -> None:
    assert doctor_roots(Scope()) == (".",)
    assert doctor_roots(Scope(("a", "b"))) == ("a", "b")
    assert doctor_roots(Scope((str(tmp_path / "a"), "b"), repository="a")) == (str(tmp_path / "a"),)


def test_a_workspace_gives_its_checkouts(tmp_path: Path) -> None:
    (tmp_path / "tadu-workspace.toml").write_text('version = 1\n[[repository]]\nkey = "shop"\n')
    (tmp_path / "tadu-workspace.local.toml").write_text(
        f'version = 1\n[paths]\nshop = "{tmp_path}"\n'
    )
    assert doctor_roots(Scope(workspace=str(tmp_path))) == (str(tmp_path),)
    with pytest.raises(WorkspaceError, match="not both"):
        doctor_roots(Scope(("a",), str(tmp_path)))
