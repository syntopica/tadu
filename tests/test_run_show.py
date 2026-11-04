import json
from pathlib import Path

import pytest

from tadu.cli import main


def repo(tmp_path: Path, name: str = "shop") -> Path:
    root = tmp_path / name
    root.mkdir()
    (root / "TODO.md").write_text("- [ ] A.\n\n  ID: t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607\n")
    return root


def first_key(root: Path, capsys: pytest.CaptureFixture[str]) -> str:
    main(["list", str(root), "--json"])
    return str(json.loads(capsys.readouterr().out.splitlines()[0])["key"])


def test_prints_text(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = repo(tmp_path)
    key = first_key(root, capsys)
    assert main(["show", key, str(root)]) == 0
    assert capsys.readouterr().out == "- [ ] A.\n\n  ID: t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607\n"


def test_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = repo(tmp_path)
    key = first_key(root, capsys)
    assert main(["show", key, str(root), "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["key"] == key


def test_unknown_key(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["show", "nope", str(repo(tmp_path))]) == 1
    assert capsys.readouterr().err == "tadu show: no item nope\n"


def test_duplicate_keys_show_first(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    one, two = repo(tmp_path, "one"), repo(tmp_path, "two")
    key = first_key(one, capsys)
    assert main(["show", key, str(one), str(two)]) == 0
    captured = capsys.readouterr()
    assert captured.err == f"tadu show: {key} matches 2 items; showing the first\n"
    assert captured.out == "- [ ] A.\n\n  ID: t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607\n"


def test_problem_and_workspace_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["show", "k", str(tmp_path / "gone")]) == 1
    assert "tadu show: gone: " in capsys.readouterr().err
    assert main(["show", "k", "--workspace", str(tmp_path)]) == 2
    assert capsys.readouterr().err.startswith("tadu show: ")
