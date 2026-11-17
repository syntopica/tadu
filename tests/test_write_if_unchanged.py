from pathlib import Path

import pytest

from tadu.write_if_unchanged import write_if_unchanged


def test_writes_when_unchanged(tmp_path: Path) -> None:
    path = tmp_path / "TODO.md"
    path.write_text("a\n")
    assert write_if_unchanged(path, "a\n", "b\n")
    assert path.read_text() == "b\n"


def test_changed_since_read_is_left_alone(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "TODO.md"
    path.write_text("edited\n")
    assert not write_if_unchanged(path, "a\n", "b\n")
    assert path.read_text() == "edited\n"
    assert "changed since tadu read it" in capsys.readouterr().err


def test_failed_write_changes_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "TODO.md"
    path.write_text("a\n")

    def fail(_target: Path, _text: str) -> None:
        raise OSError(28, "No space left on device")

    monkeypatch.setattr("tadu.write_if_unchanged.write_file_atomically", fail)
    assert not write_if_unchanged(path, "a\n", "b\n")
    assert path.read_text() == "a\n"
    assert "not written ([Errno 28] No space left on device); nothing changed" in (
        capsys.readouterr().err
    )


def test_a_missing_file_is_created_only_while_still_missing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "AGENTS.md"
    assert write_if_unchanged(path, "", "new\n")
    assert path.read_text() == "new\n"

    def appear(target: Path, _text: str) -> None:
        target.write_text("theirs\n")
        raise FileExistsError(target)

    monkeypatch.setattr("tadu.write_if_unchanged.create_file_exclusively", appear)
    other = tmp_path / "CLAUDE.md"
    assert not write_if_unchanged(other, "", "ours\n")
    assert other.read_text() == "theirs\n"
    assert "created meanwhile; nothing written, run again" in capsys.readouterr().err
