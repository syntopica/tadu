import argparse
from datetime import date
from pathlib import Path

import pytest

from tadu.doctor_command import doctor_command

TODAY = date(2026, 11, 4)


def _args(
    paths: list[str], workspace: str | None, repository: str | None = None
) -> argparse.Namespace:
    return argparse.Namespace(paths=paths, workspace=workspace, repository=repository, json=False)


def workspace(root: Path) -> Path:
    for name in ("shop", "web"):
        (root / name).mkdir()
    (root / "shop" / "TODO.md").write_text("- [ ] Fine.\n")
    (root / "web" / "TODO.md").write_text("- [x] Done here.\n")
    (root / "tadu-workspace.toml").write_text(
        'version = 1\n[[repository]]\nkey = "shop"\n[[repository]]\nkey = "web"\n'
    )
    (root / "tadu-workspace.local.toml").write_text(
        f'version = 1\n[paths]\nshop = "{root / "shop"}"\nweb = "{root / "web"}"\n'
    )
    return root


def test_the_current_directory_by_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] Fine.\n")
    monkeypatch.chdir(tmp_path)
    assert doctor_command(_args([], None), TODAY) == 0
    assert capsys.readouterr().err == ""


def test_a_broken_workspace_is_a_finding(tmp_path: Path) -> None:
    assert doctor_command(_args([], str(tmp_path)), TODAY) == 1


def test_every_repository_of_a_workspace_or_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = workspace(tmp_path)
    assert doctor_command(_args([], str(root)), TODAY) == 1
    assert "web/TODO.md" in capsys.readouterr().out
    assert doctor_command(_args([], str(root), "shop"), TODAY) == 0
    assert doctor_command(_args([], str(root), "web"), TODAY) == 1
    assert doctor_command(_args([str(root / "web"), str(root / "shop")], None, "shop"), TODAY) == 0


def test_refused_scopes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = workspace(tmp_path)
    assert doctor_command(_args(["x"], str(root)), TODAY) == 2
    assert "not both" in capsys.readouterr().err
    assert doctor_command(_args([str(root / "shop")], None, "nope"), TODAY) == 2
    assert "no repository nope" in capsys.readouterr().err
