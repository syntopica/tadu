from datetime import date
from pathlib import Path

import pytest

from tadu.load_cards import load_cards
from tadu.workspace_error import WorkspaceError

TODAY = date(2026, 11, 4)


def test_paths(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] A.\n")
    cards, problems, local = load_cards((str(tmp_path),), None, 14, TODAY)
    assert (len(cards), problems, local) == (1, (), None)


def test_default_is_current_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] A.\n- [ ] B.\n")
    monkeypatch.chdir(tmp_path)
    assert len(load_cards((), None, 14, TODAY)[0]) == 2


def test_workspace(tmp_path: Path) -> None:
    repo = tmp_path / "shop"
    repo.mkdir()
    (repo / "TODO.md").write_text("- [ ] A.\n")
    (tmp_path / "tadu-workspace.toml").write_text('version = 1\n[[repository]]\nkey = "shop"\n')
    (tmp_path / "tadu-workspace.local.toml").write_text(f'version = 1\n[paths]\nshop = "{repo}"\n')
    cards, problems, local = load_cards((), str(tmp_path), 14, TODAY)
    assert (len(cards), problems) == (1, ())
    assert local is not None


def test_both_rejected(tmp_path: Path) -> None:
    with pytest.raises(WorkspaceError, match="not both"):
        load_cards(("x",), str(tmp_path), 14, TODAY)


def test_bad_workspace(tmp_path: Path) -> None:
    with pytest.raises(WorkspaceError):
        load_cards((), str(tmp_path), 14, TODAY)
