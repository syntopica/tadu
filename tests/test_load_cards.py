from datetime import date
from pathlib import Path

import pytest

from tadu.load_cards import load_cards
from tadu.scope import Scope
from tadu.workspace_error import WorkspaceError

TODAY = date(2026, 11, 4)


def test_paths(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] A.\n")
    cards, problems, local = load_cards(Scope((str(tmp_path),)), 14, TODAY)
    assert (len(cards), problems, local) == (1, (), None)


def test_default_is_current_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] A.\n- [ ] B.\n")
    monkeypatch.chdir(tmp_path)
    assert len(load_cards(Scope(), 14, TODAY)[0]) == 2


def test_workspace(tmp_path: Path) -> None:
    repo = tmp_path / "shop"
    repo.mkdir()
    (repo / "TODO.md").write_text("- [ ] A.\n")
    (tmp_path / "tadu-workspace.toml").write_text('version = 1\n[[repository]]\nkey = "shop"\n')
    (tmp_path / "tadu-workspace.local.toml").write_text(f'version = 1\n[paths]\nshop = "{repo}"\n')
    cards, problems, local = load_cards(Scope(workspace=str(tmp_path)), 14, TODAY)
    assert (len(cards), problems) == (1, ())
    assert local is not None


def test_both_rejected(tmp_path: Path) -> None:
    with pytest.raises(WorkspaceError, match="not both"):
        load_cards(Scope(("x",), str(tmp_path)), 14, TODAY)


def test_bad_workspace(tmp_path: Path) -> None:
    with pytest.raises(WorkspaceError):
        load_cards(Scope(workspace=str(tmp_path)), 14, TODAY)


def test_one_repository_of_roots_or_of_a_workspace(tmp_path: Path) -> None:
    for name in ("shop", "web"):
        (tmp_path / name).mkdir()
        (tmp_path / name / "TODO.md").write_text(f"- [ ] {name}.\n")
    roots = (str(tmp_path / "shop"), str(tmp_path / "web"), str(tmp_path / "gone"))
    cards, problems, _ = load_cards(Scope(roots, repository="web"), 14, TODAY)
    assert ([card.item.title for card in cards], problems) == (["web."], ())
    (tmp_path / "tadu-workspace.toml").write_text(
        'version = 1\n[[repository]]\nkey = "shop"\n[[repository]]\nkey = "web"\n'
    )
    (tmp_path / "tadu-workspace.local.toml").write_text(
        f'version = 1\n[paths]\nshop = "{tmp_path / "shop"}"\nweb = "{tmp_path / "web"}"\n'
    )
    workspace = Scope(workspace=str(tmp_path), repository="shop")
    assert [card.repository for card in load_cards(workspace, 14, TODAY)[0]] == ["shop"]
    with pytest.raises(
        WorkspaceError, match="no repository nope; give --repository as one of: shop"
    ):
        load_cards(Scope(workspace=str(tmp_path), repository="nope"), 14, TODAY)
