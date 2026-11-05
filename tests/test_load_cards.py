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


def test_dependencies_resolve_across_workspace(tmp_path: Path) -> None:
    target = "t-55161023-f3a9-43a3-94df-589ca752fa13"
    for key, text in (
        ("shop", f"- [ ] A.\n\n  Depends on: {target}\n"),
        ("api", f"- [!] B.\n\n  ID: {target}\n"),
    ):
        (tmp_path / key).mkdir()
        (tmp_path / key / "TODO.md").write_text(text)
    (tmp_path / "tadu-workspace.toml").write_text(
        'version = 1\n[[repository]]\nkey = "shop"\n[[repository]]\nkey = "api"\n'
    )
    (tmp_path / "tadu-workspace.local.toml").write_text(
        f'version = 1\n[paths]\nshop = "{tmp_path / "shop"}"\napi = "{tmp_path / "api"}"\n'
    )
    cards = load_cards((), str(tmp_path), 14, TODAY)[0]
    assert [(d.id, d.repository, d.state) for d in cards[0].dependencies] == [(target, "api", "!")]


def test_dependencies_resolve_for_paths(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text(
        "- [ ] A.\n\n  Depends on: t-55161023-f3a9-43a3-94df-589ca752fa13\n"
    )
    cards = load_cards((str(tmp_path),), None, 14, TODAY)[0]
    assert cards[0].dependencies[0].state is None
