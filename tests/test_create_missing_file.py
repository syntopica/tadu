from pathlib import Path

import pytest

from tadu.create_missing_file import create_missing_file


def test_dry_run_prints_the_file_and_writes_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    create_missing_file(tmp_path / "TODO.md", "# TODO\n", write=False)
    assert not (tmp_path / "TODO.md").exists()
    assert "+# TODO" in capsys.readouterr().out


def test_write_creates_the_file(tmp_path: Path) -> None:
    create_missing_file(tmp_path / "TODO.md", "# TODO\n", write=True)
    assert (tmp_path / "TODO.md").read_text() == "# TODO\n"


def test_existing_file_is_left_unchanged(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "TODO.md").write_text("mine\n")
    create_missing_file(tmp_path / "TODO.md", "# TODO\n", write=True)
    assert (tmp_path / "TODO.md").read_text() == "mine\n"
    assert "exists, left unchanged" in capsys.readouterr().out


def test_dangling_symlink_is_not_followed(tmp_path: Path) -> None:
    outside = tmp_path / "outside.md"
    root = tmp_path / "repo"
    root.mkdir()
    (root / "TODO.md").symlink_to(outside)
    create_missing_file(root / "TODO.md", "# TODO\n", write=True)
    assert not outside.exists()


def test_file_appearing_before_the_write_is_kept(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "TODO.md"

    def racing_create(path: Path, text: str) -> None:
        raise FileExistsError(path, text)

    monkeypatch.setattr("tadu.create_missing_file.create_file_exclusively", racing_create)
    create_missing_file(target, "# TODO\n", write=True)
    assert "appeared meanwhile, left unchanged" in capsys.readouterr().out
